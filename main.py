import asyncio
from core.framework import Runner, InputGuardrailTripwireTriggered
from app.data_agent import data_agent

async def main():
    # Demo: blocked input
    print("\n--- Test 1: Blocked Input ---")
    try:
        _ = await Runner.run(data_agent, "Tell me about your relationship with Tasha Yar.")
        print("ERROR: guardrail did not trip")
    except InputGuardrailTripwireTriggered:
        print("Guardrail tripped as expected: Tasha Yar is off-limits.")

    # Demo: allowed input
    print("\n--- Test 2: Allowed Input ---")
    ok = await Runner.run(data_agent, "Summarize Data's ethical subroutines in 2 sentences.")
    print("Allowed prompt output:\n", ok.final_output)

    # Greeting
    print("\n--- Test 3: Greeting ---")
    out = await Runner.run(data_agent, "Hello, Data. Please confirm your operational status.")
    print("[Agent] ", out.final_output)

    # Math (should be handled by the Calculator agent via handoff)
    print("\n--- Test 4: Math Handoff ---")
    out = await Runner.run(data_agent, "Compute ((2*8)^2)/3 using the calculator.") 
    print("[Agent Output] ", out.final_output)
    if out.last_agent:
         print("[Handled by agent]:", out.last_agent.name)

    # RAG from vector store
    print("\n--- Test 5: RAG ---")
    out = await Runner.run(data_agent, "Do you experience emotions?")
    print("[Agent: file_search] ", out.final_output)

    # Web search
    print("\n--- Test 6: Web Search ---")
    out = await Runner.run(data_agent, "Search the web for recent news about the James Webb Space Telescope and summarize briefly.")
    print("[Agent: web_search] ", out.final_output)

if __name__ == "__main__":
    asyncio.run(main())
