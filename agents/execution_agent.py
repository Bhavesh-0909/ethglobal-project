from datetime import datetime
from uuid import uuid4

from openai import OpenAI
from uagents import Context, Protocol, Agent
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

##
### Example Expert Assistant
##
## This chat example is a barebones example of how you can create a simple chat agent
## and connect to agentverse. In this example we will be prompting the ASI-1 model to
## answer questions on a specific subject only. This acts as a simple placeholder for
## a more complete agentic system.
##

# the subject that this assistant is an expert in

client = OpenAI(
    # By default, we are using the ASI-1 LLM endpoint and model
    base_url='https://api.asi1.ai/v1',

    # You can get an ASI-1 api key by creating an account at https://asi1.ai/dashboard/api-keys
    api_key='sk_42c1b4efbd0a4e299e25898bdb151d29aebba1181f964cf19f225f6446f5cd60',
)

agent = Agent()

# We create a new protocol which is compatible with the chat protocol spec. This ensures
# compatibility between agents
protocol = Protocol(spec=chat_protocol_spec)


# We define the handler for the chat messages that are sent to your agent
@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    # send the acknowledgement for receiving the message
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )

    # collect up all the text chunks
    text = ''
    for item in msg.content:
        if isinstance(item, TextContent):
            text += item.text

    # query the model based on the user question
    # Remove the subject matter
    # subject_matter = "birds"  # ❌ Remove this

    # system prompt for execution automation agent
    system_prompt = """
    You are an intelligent execution agent. You can perform tasks, provide instructions, 
    and automate workflows for users. Answer questions and provide actionable steps 
    based on the user's request.
    """

    try:
        # query the model
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            max_tokens=2048,
        )

        response = str(r.choices[0].message.content)
    except:
        ctx.logger.exception('Error querying model')
        response = "Sorry, I encountered an error processing your request."

    # send the response back to the user
    await ctx.send(sender, ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[
            # we send the contents back in the chat message
            TextContent(type="text", text=response),
            # we also signal that the session is over, this also informs the user that we are not recording any of the
            # previous history of messages.
            EndSessionContent(type="end-session"),
        ]
    ))


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    # we are not interested in the acknowledgements for this example, but they can be useful to
    # implement read receipts, for example.
    pass


# attach the protocol to the agent
agent.include(protocol, publish_manifest=True)
