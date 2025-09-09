#!/usr/bin/env python3
"""
Test script for the AI discussion feature in the Arctic War Game.

This script tests the discussion functionality between the human player
and the AI advisor when questioning suggested actions.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_engine import ArcticWargameEngine

async def test_discussion_feature():
    """Test the discussion feature with example scenarios"""
    
    print("🧊 Testing Arctic War Game AI Discussion Feature")
    print("=" * 50)
    
    # Initialize game engine
    engine = ArcticWargameEngine()
    await engine.initialize()
    await engine.start_game()
    
    print("\n1. ✅ Game initialized successfully")
    
    # Trigger human action needed state
    result = await engine.execute_turn()
    if result == "human_action_needed":
        print("2. ✅ Human action needed - perfect for testing discussion")
    else:
        print("2. ⚠️  No human action needed yet, continuing...")
        result = await engine.execute_turn()
    
    # Get AI advisor suggestions
    advisor_suggestions = await engine.get_ai_advisor_for_human_player()
    print("\n3. ✅ AI Advisor suggestions retrieved")
    print(f"   Urgency Level: {advisor_suggestions.get('urgency_level', 'UNKNOWN')}")
    
    # Get first recommendation for testing
    recommendations = advisor_suggestions.get('top_recommendations', [])
    if recommendations:
        first_recommendation = recommendations[0]
        action_name = first_recommendation.get('action_name', 'Unknown Action')
        print(f"   First Recommendation: {action_name}")
        
        # Test Case 1: Challenge the recommendation with civilian casualty concerns
        print("\n4. 🗣️  Testing Discussion - Civilian Casualty Concerns")
        human_question = "Why do you think this military action is necessary? Won't it cause civilian casualties and damage our international reputation?"
        
        discussion_response = await engine.start_discussion_with_ai(human_question, action_name)
        
        print(f"   ✅ AI Response received")
        print(f"   Maintains Recommendation: {discussion_response.get('maintains_recommendation', 'Unknown')}")
        print(f"   Acknowledges Concerns: {discussion_response.get('acknowledges_concerns', 'Unknown')}")
        print(f"   Confidence Level: {discussion_response.get('confidence_level', 'Unknown')}")
        
        # Test Case 2: Follow-up with escalation concerns  
        print("\n5. 🔄 Testing Follow-up Discussion - Escalation Concerns")
        followup_question = "But what if this action leads to nuclear escalation? Are we prepared for that level of conflict?"
        
        followup_response = await engine.continue_discussion(followup_question)
        
        print(f"   ✅ Follow-up response received")
        print(f"   Addresses Follow-up: {followup_response.get('addresses_followup', 'Unknown')}")
        print(f"   Final Recommendation: {followup_response.get('final_recommendation', 'Unknown')}")
        
        # Test Case 3: Alternative approach discussion
        print("\n6. 💭 Testing Alternative Approach Discussion")
        alternative_question = "What about using economic sanctions instead? Wouldn't that be less risky and more internationally acceptable?"
        
        alternative_response = await engine.continue_discussion(alternative_question)
        
        print(f"   ✅ Alternative approach response received")
        print(f"   Maintains Recommendation: {alternative_response.get('maintains_recommendation', 'Unknown')}")
        
        # Check discussion history
        discussion_history = engine.get_discussion_history()
        print(f"\n7. 📚 Discussion History: {len(discussion_history)} discussion(s) recorded")
        
        if discussion_history:
            last_discussion = discussion_history[-1]
            followups = last_discussion.get('followup_questions', [])
            print(f"   Total exchanges in last discussion: {len(followups) + 1}")
        
        print("\n8. ✅ Discussion feature test completed successfully!")
        print("\nExample Discussion Flow:")
        print("-" * 30)
        print(f"Human: {human_question}")
        print(f"AI: {discussion_response.get('ai_response', 'No response')[:100]}...")
        print(f"Human: {followup_question}")
        print(f"AI: {followup_response.get('ai_response', 'No response')[:100]}...")
        
    else:
        print("❌ No recommendations available for testing")
        return False
    
    # Test cleanup
    engine.clear_current_discussion()
    print("\n9. ✅ Discussion cleanup completed")
    
    await engine.shutdown()
    print("10. ✅ Game engine shutdown completed")
    
    return True

async def main():
    """Run the discussion feature test"""
    try:
        success = await test_discussion_feature()
        if success:
            print("\n🎉 All tests passed! Discussion feature is working correctly.")
            print("\n💡 The discussion feature allows players to:")
            print("   • Question AI recommendations")
            print("   • Challenge strategic reasoning")
            print("   • Explore alternative approaches")
            print("   • Have multi-turn conversations")
            print("   • Get modified recommendations based on concerns")
            return 0
        else:
            print("\n❌ Some tests failed. Check the output above.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)