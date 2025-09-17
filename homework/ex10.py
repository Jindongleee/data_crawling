# 책상이 하루에 1개씩 판매, 현재 N개의 책상 보유
# M일에 한 번씩 도매점으로부터 책상이 1개 입고
# 책상 재고가 0이 될 떄까지 며칠이 걸리는지 계산하는 solution 함수
# 1 <= N <= 100, 현재 보유중인 책상의 개수
# 2 <= M <= 100, 일수

# 공차 -> M-1
# 초기값 a1 = N

# basic
def solution(n, m):
    count = 0
    day = 0
    count = n
    while count != 0:
        day+=1
        count -= 1
        if day % m == 0:
            count += 1

    return day


# n = int(input())
# m = int(input())
# print(solution(n,m))

# 공차 활용
# def solution(n, m):
    
#     k = 0

#     while (n - (k)*(m-1)) >= 0:
#         k += 1
    
#     if (n - (k-1)*(m-1)) == 0: #  
#         return m*(k-1)-1

#     return m*(k-1)+1 

# n=int(input())
# m = int(input())
# print(solution(n,m))


# 나머지와 몫을 계속 저장해야됨 -> 재귀 사용
# def solution(stock, M, remainder=0):
#     # 더 이상 입고가 불가능하면 종료
#     if stock + remainder < M:
#         return stock  # 남은 재고만큼 일수 추가

#     total_stock = stock + remainder
#     new_stock = total_stock // M        # 입고될 책상 수
#     new_remainder = total_stock % M     # 다음 단계 누적 나머지

#     # 현재 재고 소진 일수 + 다음 단계 재귀
#     return stock + solution(new_stock, M, new_remainder)

n=int(input())
m = int(input())
print(solution(n,m))
