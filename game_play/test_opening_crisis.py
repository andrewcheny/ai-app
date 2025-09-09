#!/usr/bin/env python3
"""
Test script for dramatic opening crisis events in Arctic warfare game
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from game_engine import ArcticWargameEngine

async def test_opening_crisis():
    """Test the dramatic opening crisis system"""
    print("🚨 Testing Dramatic Opening Crisis Events")
    print("=" * 60)
    
    # Test multiple crisis scenarios
    for test_run in range(3):
        print(f"\n🎬 CRISIS SCENARIO #{test_run + 1}")
        print("-" * 40)
        
        # Initialize and start game
        engine = ArcticWargameEngine()
        await engine.initialize()
        await engine.start_game()
        
        # Get opening crisis details
        crisis = engine.get_opening_crisis()
        if crisis:
            print(f"📺 CRISIS: {crisis['name']}")
            print(f"📖 DESCRIPTION:")
            print(f"   {crisis['description']}")
            print()
            
            print(f"🎥 VIDEO PROMPT:")
            print(f"   {crisis['video_prompt']}")
            print()
            
            print(f"⚡ IMMEDIATE CONSEQUENCES:")
            for i, consequence in enumerate(crisis['consequences'][:5], 1):
                print(f"   {i}. {consequence}")
            print()
            
            print(f"🌡️ TENSION IMPACT: +{crisis['tension_increase']}")
            print(f"💥 RESOURCE IMPACTS:")
            for nation, changes in crisis['affected_resources'].items():
                nation_name = nation.replace('_resources', '').title()
                print(f"   {nation_name}: {changes}")
            print()
            
            # Show game state after crisis
            game_state = engine.get_game_state()
            print(f"📊 POST-CRISIS GAME STATE:")
            print(f"   Turn: {game_state.turn}")
            print(f"   Tension Level: {game_state.tension_level}/10")
            print(f"   Russia: Military={game_state.russia_resources['military']}, Economic={game_state.russia_resources['economic']}, Political={game_state.russia_resources['political']}, Info={game_state.russia_resources['information']}")
            print(f"   China:  Military={game_state.china_resources['military']}, Economic={game_state.china_resources['economic']}, Political={game_state.china_resources['political']}, Info={game_state.china_resources['information']}")
            print(f"   USA:    Military={game_state.us_resources['military']}, Economic={game_state.us_resources['economic']}, Political={game_state.us_resources['political']}, Info={game_state.us_resources['information']}")
            print()
            
            print(f"📰 CRISIS EVENTS IN GAME LOG:")
            for event in game_state.recent_events:
                print(f"   • {event}")
            print()
        
        await engine.shutdown()
        
        if test_run < 2:  # Add separator between runs
            print("🔄 Generating new crisis scenario...")
    
    print("=" * 60)
    print("✅ Opening crisis testing completed!")
    print("\nThe system generates random dramatic crises that:")
    print("• Create immediate international tensions")
    print("• Affect nation resources realistically") 
    print("• Provide cinematic video prompts")
    print("• Set up compelling gameplay scenarios")

async def test_specific_oil_spill_scenario():
    """Test the specific oil spill scenario you mentioned"""
    print("\n🛢️ Testing Specific Arctic Oil Spill Scenario")
    print("=" * 60)
    
    # Force the Arctic Environmental Disaster scenario
    engine = ArcticWargameEngine()
    await engine.initialize()
    
    # Generate crisis and check if it's the oil spill
    for attempt in range(10):  # Try up to 10 times to get the oil spill scenario
        crisis = await engine.generate_opening_crisis()
        if "oil" in crisis['description'].lower() or "tanker" in crisis['description'].lower():
            print(f"🎯 Found Oil Spill Scenario (attempt {attempt + 1}):")
            print()
            print(f"📺 CRISIS NAME: {crisis['name']}")
            print()
            print(f"📖 DRAMATIC DESCRIPTION:")
            print(f"{crisis['description']}")
            print()
            print(f"🎥 CINEMATIC VIDEO PROMPT:")
            print(f"{crisis['video_prompt']}")
            print()
            print(f"⚡ GEOPOLITICAL CONSEQUENCES:")
            for i, consequence in enumerate(crisis['consequences'], 1):
                print(f"{i}. {consequence}")
            print()
            print(f"📊 CRISIS IMPACT:")
            print(f"• Tension Increase: +{crisis['tension_increase']}")
            print(f"• Resource Effects: {crisis['affected_resources']}")
            print()
            
            # This shows what the video generation prompt would be
            print("🎬 VIDEO GENERATION READY:")
            print("This prompt can be fed directly into AI video generation systems like:")
            print("• RunwayML Gen-2/Gen-3")  
            print("• Stable Video Diffusion")
            print("• Pika Labs")
            print("• Any text-to-video AI model")
            break
    else:
        print("❌ Oil spill scenario not generated in 10 attempts (random selection)")
        print("But the system includes this scenario in its crisis database")
    
    await engine.shutdown()

if __name__ == "__main__":
    asyncio.run(test_opening_crisis())
    asyncio.run(test_specific_oil_spill_scenario())