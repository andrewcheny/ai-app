#!/usr/bin/env python3
"""
Test script for enhanced dramatic Arctic gameplay with AI advisor and video prompts
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from game_engine import ArcticWargameEngine

async def test_dramatic_gameplay():
    """Test the enhanced dramatic gameplay features"""
    print("🎬 Testing Enhanced Dramatic Arctic Warfare Gameplay")
    print("=" * 60)
    
    # Initialize game engine
    engine = ArcticWargameEngine()
    await engine.initialize()
    await engine.start_game()
    
    print("🎮 Game initialized successfully!")
    print()
    
    # Execute AI turns to create some drama
    print("🤖 Executing AI turns to build tension...")
    turn_result = await engine.execute_turn()
    print(f"Turn result: {turn_result}")
    
    if turn_result == "human_action_needed":
        print("\n🇺🇸 HUMAN PLAYER TURN - US Strategic Command")
        print("=" * 50)
        
        # Get current game state
        game_state = engine.get_game_state()
        print(f"📊 Current Situation:")
        print(f"   Turn: {game_state.turn}")
        print(f"   Tension Level: {game_state.tension_level}/10")
        print(f"   US Resources: Military={game_state.us_resources['military']}, Economic={game_state.us_resources['economic']}, Political={game_state.us_resources['political']}, Information={game_state.us_resources['information']}")
        print()
        
        print("📰 Recent Events:")
        for event in game_state.recent_events[-3:]:
            print(f"   • {event}")
        print()
        
        if game_state.adversary_reactions:
            print("📡 Adversary Communications:")
            for reaction in game_state.adversary_reactions[-2:]:
                print(f"   • {reaction}")
            print()
        
        # Get AI advisor suggestions
        print("🧠 AI STRATEGIC ADVISOR ANALYSIS")
        print("-" * 40)
        try:
            advisor_analysis = await engine.get_ai_advisor_for_human_player()
            
            print(f"🚨 URGENCY LEVEL: {advisor_analysis.get('urgency_level', 'UNKNOWN')}")
            print()
            
            print("📋 THREAT ASSESSMENT:")
            print(f"   {advisor_analysis.get('threat_assessment', 'Analysis unavailable')}")
            print()
            
            print("🎯 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(advisor_analysis.get('top_recommendations', [])[:3], 1):
                print(f"   {i}. {rec.get('action_name', 'Unknown')} ({rec.get('priority', 'UNKNOWN')} PRIORITY)")
                print(f"      Rationale: {rec.get('rationale', 'No rationale provided')}")
                print()
            
            print("🔍 STRATEGIC ANALYSIS:")
            print(f"   {advisor_analysis.get('strategic_analysis', 'No analysis available')}")
            print()
            
        except Exception as e:
            print(f"❌ AI Advisor offline: {e}")
            print()
        
        # Get available actions
        available_actions = engine.get_human_actions()
        print(f"⚡ AVAILABLE TACTICAL OPTIONS ({len(available_actions)} actions):")
        print("-" * 50)
        
        for i, action in enumerate(available_actions[:5], 1):  # Show first 5
            print(f"{i}. {action['name']} ({action['type'].value.upper()})")
            print(f"   Description: {action['description']}")
            print(f"   Cost: {action['cost']}")
            if 'video_prompt' in action:
                print(f"   Video Scene: {action['video_prompt'][:100]}...")
            print()
        
        # Simulate human choosing first available action
        if available_actions:
            chosen_action = available_actions[0]
            print(f"🎯 EXECUTING: {chosen_action['name']}")
            print("-" * 40)
            
            # Execute the action
            result = await engine.execute_human_action(chosen_action)
            
            print(f"📊 Action Result: {result}")
            print()
            
            # Get generated video prompt
            video_prompt = engine.get_last_action_video_prompt()
            tactical_details = engine.get_last_action_tactical_details()
            
            if video_prompt:
                print("🎬 GENERATED VIDEO PROMPT:")
                print(f"   {video_prompt}")
                print()
            
            if tactical_details:
                print("⚙️ TACTICAL EXECUTION DETAILS:")
                print(f"   {tactical_details}")
                print()
            
            # Show updated game state
            updated_state = engine.get_game_state()
            print("📊 POST-ACTION STATUS:")
            print(f"   Tension Level: {updated_state.tension_level}/10")
            print(f"   US Resources: Military={updated_state.us_resources['military']}, Economic={updated_state.us_resources['economic']}, Political={updated_state.us_resources['political']}, Information={updated_state.us_resources['information']}")
            print()
            
            print("📰 Latest Events:")
            for event in updated_state.recent_events[-2:]:
                print(f"   • {event}")
            print()
        
    # Clean up
    await engine.shutdown()
    print("✅ Dramatic gameplay test completed!")

if __name__ == "__main__":
    asyncio.run(test_dramatic_gameplay())