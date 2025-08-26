#!/usr/bin/env python3

def icm_dp(chips, payouts):
    """
    Poker ICM (Independent Chip Model) 動態規劃計算機

    目標:
      給定 n 位玩家的籌碼 chips[i] 與名次獎金 payouts[pos] (pos=0 表示冠軍)，
      計算每位玩家的期望獎金 EV。

    狀態定義:
      mask: 以 bitmask 表示仍在場上的玩家集合，1 表示玩家存在
      pos: 目前要發放的名次(0-based)，例如 pos=0 發冠軍、pos=1 發亞軍、...
      dp[mask][pos][j]:
        在「場上玩家集合=mask」且「下一個要確定的名次=pos」的條件下，
        玩家 j 的期望獎金。

    遞迴轉移:
      設 S(mask) = sum_{k in mask} chips[k]。
      當要決定 pos 名次時，任何在場玩家 i 以機率 chips[i]/S(mask) 取得該名次，
      其立即貢獻為 payouts[pos] 給玩家 i，接著場上變為 next_mask = mask{i}，
      下一個名次為 pos+1，其他玩家的期望來自 dp[next_mask][pos+1][j]。

      故對任意玩家 j：
        dp[mask][pos][j]
          = Σ_{i in mask} ( chips[i] / S(mask) ) *
              ( [i==j] * payouts[pos] + dp[next_mask][pos+1][j] )

      其中 [i==j] 為指示函數，i==j 時為 1，否則 0。

    邊界條件:
      當 mask 為空集合時，沒有名次可發，期望皆為 0。實作上 dp 預設為 0 即可。

    回傳:
      dp[full_mask][0]，即從所有玩家起始、從冠軍名次開始計算的每位玩家期望獎金。
    """
    n = len(chips)
    assert len(payouts) == n, "Payouts length must match chips length"
    assert sorted(payouts, reverse=True) == payouts, "Payouts must be sorted in descending order"
    # dp 維度:
    # - mask: 0..(1<<n)-1
    # - pos: 0..n (需要到 n，因為會存取 pos+1)
    # - 第三維長度 n，表示每位玩家的 EV
    dp = [[[0.0] * n for _ in range(n + 1)] for _ in range(1 << n)]

    # 對所有非空 mask 進行轉移。空 mask 的行為為 0（邊界）。
    for mask in range(1, 1 << n):
        # S(mask): 場上玩家總籌碼
        total = sum(chips[i] for i in range(n) if (mask >> i) & 1)
        for pos in range(n):
            # 這一層要發放的名次是 pos
            ev = [0.0] * n  # 暫存 dp[mask][pos] 的結果向量
            for i in range(n):
                if not (mask >> i) & 1:
                    continue
                # 玩家 i 以 ICM 機率取得當前名次
                prob = chips[i] / total
                next_mask = mask ^ (1 << i)
                # 立即貢獻：若 i 拿到名次 pos，i 的 EV 增加 payouts[pos]
                ev[i] += prob * payouts[pos]
                # 未來貢獻：其餘名次的期望，從 dp[next_mask][pos+1] 帶入
                for j in range(n):
                    ev[j] += prob * dp[next_mask][pos + 1][j]
            dp[mask][pos] = ev

    # 從所有玩家都在場，且從冠軍名次開始的期望
    full_mask = (1 << n) - 1
    return dp[full_mask][0]


if __name__ == "__main__":
    # 範例：3 人、籌碼 [7000, 20000, 8000]，名次獎金 [50, 30, 20]
    # 輸出為各玩家在 ICM 下的期望獎金
    chips = [7000, 20000, 8000]
    payouts = [50, 30, 20]
    result = icm_dp(chips, payouts)
    for i, ev in enumerate(result, 1):
        print(f"Player{i} Payout after ICM: {ev:.2f}")
