import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.scripts.test_core_engine import run_core_pipeline_test

async def main():
    print("==================================================")
    print("RUNNING AIRA MASTER TEST SUITE")
    print("==================================================")
    print("\n--- 1. Testing Core Pipeline (Mock STT -> LLM -> TTS) ---")
    await run_core_pipeline_test(use_mocks=True)
    
    print("\n==================================================")
    print("ALL TEST SUITES PASSED CLEANLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
