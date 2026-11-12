"""Test môi trường mô phỏng và RL Agent. Không cần TensorFlow, Neo4j."""
from app.agents.rl_agent import FollowUpPolicyAgent
from sim.followup_env import ACTIONS, CONTENTS, FollowUpEnv, transition_probs, STATES
from sim.rl_train import compare, evaluate, greedy_policy, train

Q_CACHE = {}


def _Q():
    if "Q" not in Q_CACHE:
        Q_CACHE["Q"] = train(episodes=3000, seed=42)
    return Q_CACHE["Q"]


def test_actions_are_educational_or_follow_up_only():
    names = " ".join(CONTENTS.values()).lower()
    assert "thuốc" not in names and "liều" not in names
    assert len(ACTIONS) == 9


def test_transition_probabilities_are_valid():
    for r in STATES:
        for c, i in ACTIONS:
            up, down = transition_probs(r, c, i)
            assert 0.0 <= up <= 0.95 and 0.0 <= down <= 0.95 and up + down <= 1.0


def test_risk_stays_within_bounds():
    env = FollowUpEnv(seed=3)
    for _ in range(200):
        s = env.reset()
        for _ in range(12):
            s, _, done = env.step(ACTIONS[0])
            assert s in STATES
            if done:
                break


def test_invalid_action_is_rejected():
    env = FollowUpEnv(seed=0)
    env.reset(0)
    try:
        env.step((9, 9))
        raise AssertionError("phải báo lỗi với hành động không hợp lệ")
    except ValueError:
        pass


def test_environment_is_reproducible():
    a, b = FollowUpEnv(seed=5), FollowUpEnv(seed=5)
    assert a.reset() == b.reset()
    for act in ACTIONS * 2:
        assert a.step(act) == b.step(act)


def test_training_is_reproducible():
    assert train(episodes=200, seed=1) == train(episodes=200, seed=1)


def test_learned_policy_beats_random_in_simulation():
    res = compare(_Q(), episodes=300)
    assert res["learned_q_learning"]["mean_return"] > res["random"]["mean_return"]


def test_learned_policy_does_not_leave_high_risk_on_6_month_gap():
    policy = greedy_policy(_Q())
    assert policy[2][1] != 2


def test_agent_returns_simulated_payload_only():
    agent = FollowUpPolicyAgent(greedy_policy(_Q()))
    m = agent.run("r", 2)
    assert m.status == "ok" and m.payload["simulated"] is True
    assert "Không áp dụng cho bệnh nhân thật" in m.payload["note"]
    assert set(m.payload) == {"simulated", "risk_state", "content", "follow_up_months", "note"}


def test_agent_rejects_unknown_state_and_action():
    agent = FollowUpPolicyAgent(greedy_policy(_Q()))
    assert agent.run("r", 7).status == "error"
    bad = FollowUpPolicyAgent({0: (9, 9), 1: (0, 0), 2: (0, 0)})
    assert bad.run("r", 0).status == "error"


def test_evaluate_reports_three_metrics():
    r = evaluate(lambda s: (0, 1), episodes=20)
    assert set(r) == {"mean_return", "share_high_risk_steps", "mean_final_risk"}
