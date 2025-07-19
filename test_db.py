import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append('/home/muskiteer/Desktop/new-kairos/kairos/backend')

from agent.autonomous_agent import KairosAutonomousAgent
from database.supabase_client import supabase_client

async def test_persistence_system():
    """Test the persistence system step by step"""
    
    print("🧪 Testing Kairos Agent Persistence System")
    print("=" * 50)
    
    # 1. Test database connection
    print("\n1️⃣ Testing database connection...")
    try:
        test_session_id = "test-session-123"
        memory_data = supabase_client.get_session_memory_summary(test_session_id)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # 2. Create agent and test basic functionality
    print("\n2️⃣ Creating autonomous agent...")
    agent = KairosAutonomousAgent("test_user")
    print(f"✅ Agent created with {len(agent.memory)} initial memory entries")
    
    # 3. Start a short test session
    print("\n3️⃣ Starting test autonomous session...")
    try:
        response = await agent.process_autonomous_request("test agent for 5 minutes", "test_user")
        session_id = response["data"]["session_id"]
        print(f"✅ Test session started: {session_id}")
    except Exception as e:
        print(f"❌ Failed to start session: {e}")
        return
    
    # 4. Wait for some decisions
    print("\n4️⃣ Waiting for agent decisions...")
    await asyncio.sleep(10)  # Wait 10 seconds for first decision
    
    # 5. Check persistence
    print("\n5️⃣ Testing persistence...")
    debug_info = await agent.debug_persistence_system(session_id)
    print("Debug Info:")
    for key, value in debug_info.items():
        print(f"   {key}: {value}")
    
    # 6. Check memory and database
    print("\n6️⃣ Memory and database status...")
    print(f"   In-memory decisions: {len(agent.memory)}")
    
    try:
        memory_data = supabase_client.get_session_memory_summary(session_id)
        conversations = memory_data.get("conversations", [])
        trades = memory_data.get("trades", [])
        strategies = memory_data.get("strategies", [])
        
        print(f"   Database conversations: {len(conversations)}")
        print(f"   Database trades: {len(trades)}")
        print(f"   Database strategies: {len(strategies)}")
        
        if conversations:
            print("   Sample conversation:")
            print(f"      Content: {conversations[0].get('content', 'N/A')[:100]}...")
            print(f"      Reasoning: {conversations[0].get('reasoning', 'N/A')[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Error checking database: {e}")
    
    # 7. Test agent restart (simulate persistence)
    print("\n7️⃣ Testing agent restart persistence...")
    
    # Create new agent (simulate restart)
    new_agent = KairosAutonomousAgent("test_user")
    print(f"   New agent initial memory: {len(new_agent.memory)}")
    
    # Load session memory
    try:
        await new_agent.load_session_memory(session_id)
        print(f"   New agent memory after loading: {len(new_agent.memory)}")
        
        if len(new_agent.memory) > 0:
            print("   ✅ Persistence working - memory restored!")
        else:
            print("   ⚠️  No memory restored - either no decisions made yet or persistence issue")
    except Exception as e:
        print(f"   ❌ Error loading memory: {e}")
    
    # 8. Get learning stats
    print("\n8️⃣ Getting learning statistics...")
    try:
        stats = await agent.get_session_learning_stats(session_id)
        print("   Learning Stats:")
        for key, value in stats.items():
            print(f"      {key}: {value}")
    except Exception as e:
        print(f"   ❌ Error getting stats: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")
    print("\nKey indicators of successful persistence:")
    print("• 'Decision persisted to DB' messages in logs")
    print("• Database conversations/trades > 0")
    print("• Memory restored after agent restart")
    print("• No 'session_id None' errors")

if __name__ == "__main__":
    asyncio.run(test_persistence_system())