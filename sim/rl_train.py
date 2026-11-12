"""Huấn luyện Q-learning dạng bảng và đánh giá chính sách trong mô phỏng. Chỉ dùng thư viện chuẩn."""
import random
from sim.followup_env import ACTIONS, FollowUpEnv, GAMMA, STATES, HORIZON


def train(episodes: int = 5000, seed: int = 42, alpha: float = 0.1, gamma: float = GAMMA,
          eps_start: float = 1.0, eps_min: float = 0.05) -> dict:
    rng = random.Random(seed)
    env = FollowUpEnv(seed=seed)
    Q = {(s, a): 0.0 for s in STATES for a in ACTIONS}
    for ep in range(episodes):
        eps = max(eps_min, eps_start * (1 - ep / episodes))
        s = env.reset()
        for _ in range(HORIZON):
            if rng.random() < eps:
                a = rng.choice(ACTIONS)
            else:
                a = max(ACTIONS, key=lambda x: Q[(s, x)])
            s2, r, done = env.step(a)
            target = r + (0.0 if done else gamma * max(Q[(s2, x)] for x in ACTIONS))
            Q[(s, a)] += alpha * (target - Q[(s, a)])
            s = s2
            if done:
                break
    return Q


def greedy_policy(Q: dict) -> dict:
    return {s: max(ACTIONS, key=lambda x: Q[(s, x)]) for s in STATES}


def evaluate(policy_fn, episodes: int = 500, seed: int = 1234, gamma: float = GAMMA) -> dict:
    """Mọi chính sách được đánh giá trên cùng chuỗi ngẫu nhiên (common random numbers)."""
    env = FollowUpEnv(seed=seed)
    returns, high_steps, final_risk, steps = [], 0, 0, 0
    for _ in range(episodes):
        s = env.reset()
        total = 0.0
        for t in range(HORIZON):
            a = policy_fn(s)
            s, r, done = env.step(a)
            total += (gamma ** t) * r
            steps += 1
            high_steps += 1 if s == 2 else 0
            if done:
                break
        returns.append(total)
        final_risk += s
    return {"mean_return": round(sum(returns) / len(returns), 4),
            "share_high_risk_steps": round(high_steps / steps, 4),
            "mean_final_risk": round(final_risk / episodes, 4)}


def compare(Q: dict, episodes: int = 500) -> dict:
    """So sánh bốn chính sách: ngẫu nhiên, cố định (6 tháng, không nội dung), quy tắc đơn giản, học được."""
    policy = greedy_policy(Q)
    rng = random.Random(7)
    simple = {0: (0, 2), 1: (1, 1), 2: (1, 0)}      # nguy cơ thấp: 6 tháng; trung bình: lối sống 3 tháng; cao: lối sống 1 tháng
    return {
        "random": evaluate(lambda s: rng.choice(ACTIONS), episodes),
        "fixed_6_months_no_content": evaluate(lambda s: (0, 2), episodes),
        "simple_rule": evaluate(lambda s: simple[s], episodes),
        "learned_q_learning": evaluate(lambda s: policy[s], episodes),
    }
