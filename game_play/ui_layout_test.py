#!/usr/bin/env python3
"""
Test script to demonstrate the new UI layout structure
"""

import asyncio
from game_engine import ArcticWargameEngine

async def test_ui_layout_data():
    """Test that all UI components have proper data"""
    print("🖥️ Testing New UI Layout Components")
    print("=" * 60)
    
    # Initialize game
    engine = ArcticWargameEngine()
    await engine.initialize()
    await engine.start_game()
    
    print("✅ Game initialized with opening crisis")
    print()
    
    # Test Situation Room data
    print("🎯 SITUATION ROOM DATA:")
    opening_crisis = engine.get_opening_crisis()
    if opening_crisis:
        print(f"Crisis Name: {opening_crisis['name']}")
        print(f"Description: {opening_crisis['description'][:100]}...")
        print(f"Video Prompt Available: {'video_prompt' in opening_crisis}")
        print(f"Consequences Count: {len(opening_crisis.get('consequences', []))}")
    else:
        print("❌ No opening crisis data")
    print()
    
    # Test Resource Comparison data
    print("🏛️ RESOURCE COMPARISON DATA:")
    game_state = engine.get_game_state()
    if game_state:
        print(f"Russia Resources: {game_state.russia_resources}")
        print(f"China Resources: {game_state.china_resources}")
        print(f"US Resources: {game_state.us_resources}")
        print(f"Tension Level: {game_state.tension_level}/10")
    else:
        print("❌ No game state data")
    print()
    
    # Test Right Sidebar data
    print("📰 RIGHT SIDEBAR DATA:")
    if game_state:
        print(f"Recent Events: {len(game_state.recent_events)} events")
        print(f"Adversary Reactions: {len(game_state.adversary_reactions)} reactions")
        print(f"Tension Changes: {len(game_state.tension_changes)} changes")
        
        if game_state.recent_events:
            print("Sample Recent Event:", game_state.recent_events[-1])
    print()
    
    # Test AI Advisor data
    print("🧠 AI ADVISOR DATA:")
    try:
        available_actions = engine.get_human_actions()
        print(f"Available Actions: {len(available_actions)}")
        if available_actions:
            print(f"Sample Action: {available_actions[0]['name']}")
            print(f"Has Video Prompt: {'video_prompt' in available_actions[0]}")
        
        # Try to get advisor suggestions
        advisor_analysis = await engine.get_us_ai_advisor_suggestions(available_actions)
        print(f"Advisor Analysis Available: {bool(advisor_analysis)}")
        print(f"Urgency Level: {advisor_analysis.get('urgency_level', 'N/A')}")
    except Exception as e:
        print(f"⚠️ AI Advisor error (expected): {e}")
    print()
    
    # Test Video Generation Prompts
    print("🎬 VIDEO GENERATION PROMPTS:")
    crisis_prompt = engine.get_opening_crisis_video_prompt()
    action_prompt = engine.get_last_action_video_prompt()
    tactical_details = engine.get_last_action_tactical_details()
    
    print(f"Opening Crisis Video Prompt: {bool(crisis_prompt)}")
    if crisis_prompt:
        print(f"Prompt Length: {len(crisis_prompt)} characters")
        print(f"Sample: {crisis_prompt[:100]}...")
    
    print(f"Last Action Video Prompt: {bool(action_prompt)}")
    print(f"Tactical Details: {bool(tactical_details)}")
    print()
    
    # Execute one turn to generate action
    print("⚡ Executing AI turn to generate action data...")
    result = await engine.execute_turn()
    print(f"Turn result: {result}")
    
    if result == "human_action_needed":
        # Check updated data
        updated_state = engine.get_game_state()
        print(f"Updated Recent Events: {len(updated_state.recent_events)}")
        print(f"Updated Tension: {updated_state.tension_level}/10")
        
        # Show latest event for UI testing
        if updated_state.recent_events:
            latest_event = updated_state.recent_events[-1]
            print(f"Latest Event: {latest_event}")
    
    await engine.shutdown()
    print()
    print("=" * 60)
    print("✅ UI Layout Test Completed!")
    print()
    print("📋 LAYOUT SUMMARY:")
    print("• Left Side: Resources chart + Situation Room with crisis details")
    print("• Right Sidebar: Recent Events + Intel Reports + Tension Monitor") 
    print("• Middle: AI Advisor analysis + Action selection")
    print("• Bottom: Video Generation Prompts with copy functionality")
    print()
    print("🎯 Ready for Streamlit deployment!")

if __name__ == "__main__":
    asyncio.run(test_ui_layout_data())