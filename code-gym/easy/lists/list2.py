if __name__ == '__main__':
    n = int(input())
    arr = map(int, input().split())
    
    runner_score = list(set(arr))
    runner_score.sort()
    
    print(runner_score[-2])
