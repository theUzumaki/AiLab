from typing import Dict

from ray.rllib.policy.policy import PolicySpec
from customEnv import KillerVictimEnv

from gymnasium import spaces

def policy_map_fn(agent_id: str, _episode=None, _worker=None, **_kwargs) -> str:
    """
    Maps agent_id to policy_id
    """
    if 'killer' in agent_id:
        return 'killer'
    elif 'victim' in agent_id:
        return 'victim'
    else:
        raise RuntimeError(f'Invalid agent_id: {agent_id}')


def get_multiagent_policies() -> Dict[str,PolicySpec]:
    policies: Dict[str,PolicySpec] = {}  # policy_id to policy_spec

    obs_spaces = spaces.Dict(
        {
            "killer": spaces.Box(low=-0, high=100, shape=(10, 5)),
            "victim": spaces.Box(low=-0, high=100, shape=(10, 5)),
        }
    )

    policies['killer'] = PolicySpec(
                policy_class=None,
                observation_space=obs_spaces['killer'],
                action_space=spaces.Discrete(5),
                config={}
    )

    policies['victim'] = PolicySpec(
        policy_class=None,
        observation_space=obs_spaces['victim'],
        action_space=spaces.Discrete(6),
        config={}
    )

    return policies
