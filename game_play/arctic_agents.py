import asyncio
import random
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field

from autogen_core import (
    CancellationToken,
    DefaultTopicId,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    message_handler,
    type_subscription,
)
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    SystemMessage,
    UserMessage,
)

class ActionType(Enum):
    DIPLOMATIC = "diplomatic"
    ECONOMIC = "economic"
    MILITARY = "military"
    INFORMATION = "information"
    CYBER = "cyber"
    INTELLIGENCE = "intelligence"
    HYBRID = "hybrid"

class GameState(BaseModel):
    turn: int = 1
    tension_level: int = 3
    russia_resources: Dict[str, int] = Field(default_factory=lambda: {"military": 8, "economic": 5, "political": 7, "information": 6})
    china_resources: Dict[str, int] = Field(default_factory=lambda: {"military": 6, "economic": 9, "political": 6, "information": 7})
    us_resources: Dict[str, int] = Field(default_factory=lambda: {"military": 9, "economic": 7, "political": 8, "information": 8})
    recent_events: List[str] = Field(default_factory=list)
    adversary_reactions: List[str] = Field(default_factory=list)
    tension_changes: List[str] = Field(default_factory=list)

class GameStateMessage(BaseModel):
    game_state: GameState

class ActionMessage(BaseModel):
    agent: str
    action_type: ActionType
    action_name: str
    target: str
    description: str
    cost: Dict[str, int]

class ActionResultMessage(BaseModel):
    action: ActionMessage
    success: bool
    consequences: List[str]
    tension_change: int

@type_subscription("arctic_game")
class ArcticGameMaster(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient):
        super().__init__("Game Master for Arctic Resource Competition scenario")
        self._model_client = model_client
        self._game_state = GameState()
        self._actions_this_turn = []
        
    @message_handler
    async def handle_action(self, message: ActionMessage, ctx: MessageContext) -> None:
        self._actions_this_turn.append(message)
        
        # Process action and determine outcome
        success = self._calculate_action_success(message)
        consequences = await self._generate_consequences(message, success)
        tension_change = self._calculate_tension_change(message, success)
        
        # Update game state
        self._update_resources(message)
        self._game_state.tension_level = max(1, min(10, self._game_state.tension_level + tension_change))
        self._game_state.recent_events.extend(consequences)
        
        # Keep only last 5 events
        self._game_state.recent_events = self._game_state.recent_events[-5:]
        
        result = ActionResultMessage(
            action=message,
            success=success,
            consequences=consequences,
            tension_change=tension_change
        )
        
        # Broadcast result to all agents
        await self.publish_message(result, topic_id=DefaultTopicId("arctic_game"))
    
    def _calculate_action_success(self, action: ActionMessage) -> bool:
        # Base success rate modified by tension and resources
        base_rate = 0.7
        tension_modifier = (10 - self._game_state.tension_level) * 0.05
        return random.random() < (base_rate + tension_modifier)
    
    async def _generate_consequences(self, action: ActionMessage, success: bool) -> List[str]:
        outcome = "succeeds" if success else "fails"
        return [f"{action.agent} {action.action_name} {outcome}: {action.description}"]
    
    def _calculate_tension_change(self, action: ActionMessage, success: bool) -> int:
        if action.action_type == ActionType.MILITARY:
            return 2 if success else 1
        elif action.action_type == ActionType.DIPLOMATIC:
            return -1 if success else 0
        return 0
    
    def _update_resources(self, action: ActionMessage) -> None:
        resources = self._get_agent_resources(action.agent)
        for resource, cost in action.cost.items():
            if resource in resources:
                resources[resource] = max(0, resources[resource] - cost)
    
    def _get_agent_resources(self, agent: str) -> Dict[str, int]:
        if "russia" in agent.lower():
            return self._game_state.russia_resources
        elif "china" in agent.lower():
            return self._game_state.china_resources
        elif "us" in agent.lower():
            return self._game_state.us_resources
        return {}
    
    async def start_new_turn(self) -> None:
        self._game_state.turn += 1
        self._actions_this_turn = []
        
        # Add random events occasionally
        if random.random() < 0.3:
            events = [
                "Massive oil deposit discovered in disputed Arctic waters",
                "Climate change accelerates Arctic ice melting",
                "International Arctic Council calls emergency meeting",
                "Commercial shipping vessel reports harassment by military patrol",
                "Environmental activists protest Arctic drilling operations"
            ]
            self._game_state.recent_events.append(random.choice(events))
        
        await self.publish_message(
            GameStateMessage(game_state=self._game_state), 
            topic_id=DefaultTopicId("arctic_game")
        )
    
    def get_game_state(self) -> GameState:
        return self._game_state

@type_subscription("arctic_game")
class RussianAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient):
        super().__init__("Russian Federation Arctic Strategy Agent")
        self._model_client = model_client
        self._name = "Russia"
        
    @message_handler
    async def handle_game_state(self, message: GameStateMessage, ctx: MessageContext) -> None:
        action = await self._decide_action(message.game_state)
        if action:
            await self.publish_message(action, topic_id=DefaultTopicId("arctic_game"))
    
    async def _decide_action(self, game_state: GameState) -> Optional[ActionMessage]:
        if not self._model_client:
            # Fallback to simple decision if no model available
            return await self._fallback_decision(game_state)
        
        # Create Putin advisor prompt
        system_prompt = """You are the most trusted advisor to Russian President Vladimir Putin for Arctic strategy. Your role is to make strategic decisions to advance Russia's interests and counter Western influence based on current developments.

You will adhere to Putin's core objectives:
- Assert Russia's dominance as the preeminent Arctic power
- Protect Russia's territorial claims and natural resources
- Counter NATO expansion and US hegemony in the Arctic
- Leverage Russia's geographic advantages and military capabilities  
- Strengthen strategic partnership with China while maintaining independence
- Use all available tools: military force, energy leverage, cyber operations, information warfare, and hybrid tactics
- Project strength and resolve to deter adversaries
- Exploit Western divisions and weaknesses

Your decisions should be bold, assertive, and advance Russia's position as the dominant Arctic power."""

        # Create situational context
        recent_events = "\n".join(game_state.recent_events[-5:]) if game_state.recent_events else "No recent events"
        adversary_reactions = "\n".join(game_state.adversary_reactions[-3:]) if game_state.adversary_reactions else "No adversary reactions"
        
        user_prompt = f"""CURRENT SITUATION:
Turn: {game_state.turn}
Tension Level: {game_state.tension_level}/10

RUSSIA'S RESOURCES:
Military: {game_state.russia_resources.get('military', 0)}
Economic: {game_state.russia_resources.get('economic', 0)}
Political: {game_state.russia_resources.get('political', 0)}
Information: {game_state.russia_resources.get('information', 0)}

ADVERSARY POSITIONS:
China - Military: {game_state.china_resources.get('military', 0)}, Economic: {game_state.china_resources.get('economic', 0)}, Political: {game_state.china_resources.get('political', 0)}, Information: {game_state.china_resources.get('information', 0)}
USA - Military: {game_state.us_resources.get('military', 0)}, Economic: {game_state.us_resources.get('economic', 0)}, Political: {game_state.us_resources.get('political', 0)}, Information: {game_state.us_resources.get('information', 0)}

RECENT DEVELOPMENTS:
{recent_events}

ADVERSARY REACTIONS:
{adversary_reactions}

Based on this situation, what action should Russia take to assert its Arctic dominance and counter Western interference?

Respond with a JSON object containing:
{{
    "action_type": "diplomatic|economic|military|information|cyber|intelligence|hybrid",
    "action_name": "Brief name for the action",
    "target": "Primary target/region of action", 
    "description": "Detailed description of what Russia will do",
    "cost": {{"resource_type": amount, ...}},
    "reasoning": "Strategic rationale for this decision"
}}

Available resource types: military, economic, political, information
Cost should not exceed available resources. Be aggressive and strategic - you are not limited to predefined actions."""

        try:
            messages = [
                SystemMessage(source="system", content=system_prompt),
                UserMessage(source="user", content=user_prompt)
            ]
            
            response = await self._model_client.create(messages=messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            import json
            try:
                action_data = json.loads(response_text)
                
                # Validate the action can be afforded
                resources = game_state.russia_resources
                if self._can_afford_action(resources, action_data.get("cost", {})):
                    return ActionMessage(
                        agent=self._name,
                        action_type=ActionType(action_data["action_type"]),
                        action_name=action_data["action_name"],
                        target=action_data["target"],
                        description=action_data["description"],
                        cost=action_data["cost"]
                    )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error parsing Russian agent response: {e}")
                return await self._fallback_decision(game_state)
                
        except Exception as e:
            print(f"Error in Russian agent LLM call: {e}")
            return await self._fallback_decision(game_state)
        
        return None
    
    def _can_afford_action(self, resources: Dict[str, int], costs: Dict[str, int]) -> bool:
        """Check if Russia can afford the proposed action"""
        for resource, cost in costs.items():
            if resources.get(resource, 0) < cost:
                return False
        return True
    
    async def _fallback_decision(self, game_state: GameState) -> Optional[ActionMessage]:
        """Fallback to hardcoded actions if LLM fails"""
        available_actions = [
            {
                "type": ActionType.MILITARY,
                "name": "Deploy Arctic Fleet",
                "target": "Northern Sea Route",
                "description": "Increases naval presence along Arctic shipping lanes",
                "cost": {"military": 2, "economic": 1}
            },
            {
                "type": ActionType.ECONOMIC,
                "name": "Expand Gas Infrastructure", 
                "target": "Yamal Peninsula",
                "description": "Builds new LNG terminals and pipelines",
                "cost": {"economic": 3}
            },
            {
                "type": ActionType.CYBER,
                "name": "Arctic Cyber Warfare",
                "target": "US Arctic Infrastructure",
                "description": "Conducts cyber attacks on US Arctic communications and navigation systems",
                "cost": {"information": 2, "military": 1}
            }
        ]
        
        # Simple decision logic - choose action we can afford
        resources = game_state.russia_resources
        for action_data in available_actions:
            can_afford = all(resources.get(res, 0) >= cost for res, cost in action_data["cost"].items())
            if can_afford:
                return ActionMessage(
                    agent=self._name,
                    action_type=action_data["type"],
                    action_name=action_data["name"],
                    target=action_data["target"],
                    description=action_data["description"],
                    cost=action_data["cost"]
                )
        return None

@type_subscription("arctic_game")
class ChineseAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient):
        super().__init__("Chinese Arctic Economic Strategy Agent")
        self._model_client = model_client
        self._name = "China"
        
    @message_handler
    async def handle_game_state(self, message: GameStateMessage, ctx: MessageContext) -> None:
        action = await self._decide_action(message.game_state)
        if action:
            await self.publish_message(action, topic_id=DefaultTopicId("arctic_game"))
    
    async def _decide_action(self, game_state: GameState) -> Optional[ActionMessage]:
        if not self._model_client:
            # Fallback to simple decision if no model available
            return await self._fallback_decision(game_state)
        
        # Create Xi Jinping advisor prompt
        system_prompt = """You are the most trusted advisor to Chinese President Xi Jinping for Arctic strategy. Your role is to make strategic decisions to advance China's interests and counter the United States based on current developments.

You will adhere to Xi Jinping's core objectives:
- Establish China as a major Arctic power despite not being an Arctic state
- Advance the Polar Silk Road initiative as part of Belt and Road
- Secure access to Arctic shipping routes and natural resources
- Counter US hegemony and build alternative partnerships
- Use all available tools: diplomatic, military, economic, cyber, information, and hybrid warfare
- Strengthen China-Russia strategic partnership in Arctic region
- Project strength while maintaining plausible deniability

Your decisions should be pragmatic, strategic, and advance China's long-term Arctic interests."""

        # Create situational context
        recent_events = "\n".join(game_state.recent_events[-5:]) if game_state.recent_events else "No recent events"
        adversary_reactions = "\n".join(game_state.adversary_reactions[-3:]) if game_state.adversary_reactions else "No adversary reactions"
        
        user_prompt = f"""CURRENT SITUATION:
Turn: {game_state.turn}
Tension Level: {game_state.tension_level}/10

CHINA'S RESOURCES:
Military: {game_state.china_resources.get('military', 0)}
Economic: {game_state.china_resources.get('economic', 0)}
Political: {game_state.china_resources.get('political', 0)}
Information: {game_state.china_resources.get('information', 0)}

ADVERSARY POSITIONS:
Russia - Military: {game_state.russia_resources.get('military', 0)}, Economic: {game_state.russia_resources.get('economic', 0)}, Political: {game_state.russia_resources.get('political', 0)}, Information: {game_state.russia_resources.get('information', 0)}
USA - Military: {game_state.us_resources.get('military', 0)}, Economic: {game_state.us_resources.get('economic', 0)}, Political: {game_state.us_resources.get('political', 0)}, Information: {game_state.us_resources.get('information', 0)}

RECENT DEVELOPMENTS:
{recent_events}

ADVERSARY REACTIONS:
{adversary_reactions}

Based on this situation, what action should China take to advance its Arctic interests and counter US influence?

Respond with a JSON object containing:
{{
    "action_type": "diplomatic|economic|military|information|cyber|intelligence|hybrid",
    "action_name": "Brief name for the action",
    "target": "Primary target/region of action",
    "description": "Detailed description of what China will do",
    "cost": {{"resource_type": amount, ...}},
    "reasoning": "Strategic rationale for this decision"
}}

Available resource types: military, economic, political, information
Cost should not exceed available resources. Be creative and strategic - you are not limited to predefined actions."""

        try:
            messages = [
                SystemMessage(source="system", content=system_prompt),
                UserMessage(source="user", content=user_prompt)
            ]
            
            response = await self._model_client.create(messages=messages)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            import json
            try:
                action_data = json.loads(response_text)
                
                # Validate the action can be afforded
                resources = game_state.china_resources
                if self._can_afford_action(resources, action_data.get("cost", {})):
                    return ActionMessage(
                        agent=self._name,
                        action_type=ActionType(action_data["action_type"]),
                        action_name=action_data["action_name"],
                        target=action_data["target"],
                        description=action_data["description"],
                        cost=action_data["cost"]
                    )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error parsing Chinese agent response: {e}")
                return await self._fallback_decision(game_state)
                
        except Exception as e:
            print(f"Error in Chinese agent LLM call: {e}")
            return await self._fallback_decision(game_state)
        
        return None
    
    def _can_afford_action(self, resources: Dict[str, int], costs: Dict[str, int]) -> bool:
        """Check if China can afford the proposed action"""
        for resource, cost in costs.items():
            if resources.get(resource, 0) < cost:
                return False
        return True
    
    async def _fallback_decision(self, game_state: GameState) -> Optional[ActionMessage]:
        """Fallback to hardcoded actions if LLM fails"""
        available_actions = [
            {
                "type": ActionType.ECONOMIC,
                "name": "Polar Silk Road Investment",
                "target": "Arctic Infrastructure", 
                "description": "Invests in ports and shipping facilities",
                "cost": {"economic": 3}
            },
            {
                "type": ActionType.DIPLOMATIC,
                "name": "Partner with Arctic Nations",
                "target": "Norway/Iceland",
                "description": "Negotiates resource extraction agreements",
                "cost": {"political": 2, "economic": 1}
            },
            {
                "type": ActionType.CYBER,
                "name": "Arctic Cyber Operations",
                "target": "US Infrastructure",
                "description": "Conducts reconnaissance on US Arctic communications",
                "cost": {"information": 2}
            }
        ]
        
        resources = game_state.china_resources
        for action_data in available_actions:
            can_afford = all(resources.get(res, 0) >= cost for res, cost in action_data["cost"].items())
            if can_afford:
                return ActionMessage(
                    agent=self._name,
                    action_type=action_data["type"],
                    action_name=action_data["name"],
                    target=action_data["target"],
                    description=action_data["description"],
                    cost=action_data["cost"]
                )
        return None

@type_subscription("arctic_game")
class USAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient):
        super().__init__("United States Arctic Security Agent")
        self._model_client = model_client
        self._name = "United States"
        
    @message_handler
    async def handle_game_state(self, message: GameStateMessage, ctx: MessageContext) -> None:
        action = await self._decide_action(message.game_state)
        if action:
            await self.publish_message(action, topic_id=DefaultTopicId("arctic_game"))
    
    async def _decide_action(self, game_state: GameState) -> Optional[ActionMessage]:
        # US prioritizes maintaining balance of power and alliance coordination
        available_actions = [
            {
                "type": ActionType.MILITARY,
                "name": "NATO Arctic Exercise",
                "target": "Allied Nations",
                "description": "Conducts joint military exercises with Nordic allies",
                "cost": {"military": 2, "political": 1}
            },
            {
                "type": ActionType.DIPLOMATIC,
                "name": "Freedom of Navigation",
                "target": "International Waters",
                "description": "Asserts rights to Arctic shipping lanes",
                "cost": {"political": 2}
            },
            {
                "type": ActionType.ECONOMIC,
                "name": "Counter Investment Program",
                "target": "Allied Infrastructure",
                "description": "Funds alternative to Chinese Belt and Road",
                "cost": {"economic": 4}
            }
        ]
        
        resources = game_state.us_resources
        for action_data in available_actions:
            can_afford = all(resources.get(res, 0) >= cost for res, cost in action_data["cost"].items())
            if can_afford:
                return ActionMessage(
                    agent=self._name,
                    action_type=action_data["type"],
                    action_name=action_data["name"],
                    target=action_data["target"],
                    description=action_data["description"],
                    cost=action_data["cost"]
                )
        return None