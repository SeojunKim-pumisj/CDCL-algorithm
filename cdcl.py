def init():
    # 할당값이 들어갈 딕셔너리
    symbolic_exp = {}

    # CNF 저장 형식 [[cluase], [cluase], ...] 각 cluase는 [1, -2, 3]으로 저장. 내부 리스트끼리는 conjunctive로 연결되어있음
    clauses = []

    while True:
        line = input("절 입력 (1 -2 3 형식) 입력이 끝나면 아무것도 입력하지 않고 엔터\n> ")
        if not line:
            break
        clause = list(map(int, line.split()))

        symbolic_exp.update({abs(var): None for var in clause})  # 입력과 동시에 None으로 초기화. 각 수식은 양수로 관리
        print(symbolic_exp)

        levels = {abs(var): -1 for var in symbolic_exp}      # 해당 할당이 어느 시점에 이뤄졌는지
        reasons = {abs(var): None for var in symbolic_exp}   # 해당 할당이 어떤 할당에 의해 이뤄졌는지

        clauses.append(clause)

    print(f'입력된 CNF {clauses}')

    return symbolic_exp, clauses, levels, reasons

def assignRandExp(exps, levels, current_level, trail):
    print(f'------------레벨 {current_level} 할당 시작------------')
    selected = None

    # assignment가 안된 수식 중 하나 골라서 true 넣기
    for key, value in exps.items():
        if value is None:
            selected = key
            exps[key] = True
            levels[key] = current_level
            trail.append(key)
            break
    
    print(f'선택된 리터럴: {selected}: {exps[selected]}')

def unitPropagation(exps, clauses, current_level, levels, reasons, trail):
    print('--------------프로파게이션 시작--------------')
    
    # propagation이 연쇄적으로 일어날 수 있으므로 변화가 없을 때까지 반복
    while True:
        changed = False
        for clause in clauses:
            print(f'선택된 절: {clause}')
            none_literals = []
            is_already_true = False

            for literal in clause:
                var = abs(literal)        # 심볼릭 수식
                val = exps[var]     # 그 수식의 실제 값

                if val is None:
                    none_literals.append(literal)
                    continue
                
                # literal엔 음수 양수로 표시되어있고, val에는 true, false가 있다. 따라서 실제 값으로 변환
                if literal < 0:
                    actual_val = not val
                else:
                    actual_val = val

                if actual_val is True:
                    is_already_true = True
                    break
            
            # true가 있는 경우 이미 프로파게이션이 불가능
            if is_already_true:
                print('프로파게이션 불가능\n==============')
                continue
            
            # 모든 리터럴이 false라면 conflict. backjumping 필요
            if not none_literals:
                print(f'{clause}에서 conflict')
                return clause

            # cluase를 다 돌고 여기까지 왔을 때 none값이 단 한 개라면 무조건 True여야한다
            if len(none_literals) == 1:
                var = abs(none_literals[0])

                # 만약 남은 하나의 수식이 양수면 그대로 True, 음수면 False로 변환해서 저장 (-3이 true여야한다면 3은 false여야한다)
                exps[var] = (none_literals[0] > 0)
                print(f'선택된 수식: {var}:{exps[var]}')

                levels[var] = current_level
                reasons[var] = clause
                trail.append(var)
                changed = True
        if not changed: break

    return None

# 충돌난 절 부터 거꾸로 올라가 현재 레벨과 같은 할당이 하나 남을 때까지 반복해서 1UIP를 찾는다
# 위로 올라갈 때는 레벨이 높은 순서대로, 같은 레벨이라면 trail을 역추적해서 가장 나중에 할당된거 찾기
def find1UIP(conflict_clause, levels, reasons, current_level, trail):
    print('=============1UIP 탐색 시작=============')
    conflict_clause = list(conflict_clause)

    trail_index = len(trail) - 1

    while True:

        # 현재 레벨과 같은 리터럴 찾기
        current_level_literals = []
        for literal in conflict_clause:
            var = abs(literal)
            if levels[var] == current_level:
                current_level_literals.append(literal)

        # 리터럴이 1개 이하라면 1UIP
        if len(current_level_literals) <= 1:
            break
        
        # 할당을 역추적하면서 충돌절에 있는 가장 최근 할당을 탐색
        while abs(trail[trail_index]) not in [abs(lit) for lit in conflict_clause]:
            trail_index -= 1

        target_var = abs(trail[trail_index])
        target_literal = None
        for literal in conflict_clause:
            if abs(literal) == target_var:
                target_literal = literal
                break

        # 가장 최근 할당에 대해서 강제했던 절
        reason = reasons[target_var]

        # 충돌난 절과 그 원인 절을 합친다
        combined = set(conflict_clause) | set(reason)

        # 두 절에서 모순이 일어나는 타겟 리터럴을 제거
        if target_literal in combined:
            combined.remove(target_literal)
        if -target_literal in combined:
            combined.remove(-target_literal)

        conflict_clause = list(combined)
        trail_index -= 1

    # 이제 conflict_cluase에 현재 레벨 리터럴이 하나만 남았다
    # 현재 레벨을 제외하고 이 절의 리터럴중 가장 높은 레벨을 찾는다
    backjump_level = 0
    for literal in conflict_clause:
        var = abs(literal)
        level = levels[var]
        if level < current_level and level > backjump_level:
            backjump_level = level

    return conflict_clause, backjump_level

def backjump(trail, levels, exps, reasons, jump_level):
    new_trail = []

    # 기존 trail을 돌면서 점프해야하는 레벨 이후의 수식은 초기화해준다
    for var in trail:
        if levels[var] <= jump_level:
            new_trail.append(var)
        else:
            exps[var] = None
            levels[var] = -1
            reasons[var] = None
    
    return new_trail




# 메인

symbolic_exp, clauses, levels, reasons = init()

# 가장 최근 값 추적용 리스트
trail = []
current_level = 0

isSatisfiable = None

# 모든 값이 할당될 때까지
while None in symbolic_exp.values() :
    # 만약 한 절에 하나의 수식만 있다면? 바로 값이 정해질 수 있기 때문에 프로파게이션을 먼저 해준다
    # 또한 백점핑 이후에 학습된 절로 인해 또 충돌이 나는지 먼저 확인해야함
    conflict_clause = unitPropagation(symbolic_exp, clauses, current_level, levels, reasons, trail)

    if conflict_clause is not None:
        if current_level == 0:
            isSatisfiable = False
            break

        learned_clause, jump_level = find1UIP(conflict_clause, levels, reasons, current_level, trail)
        clauses.append(learned_clause)
        trail = backjump(trail, levels, symbolic_exp, reasons, jump_level)
        current_level = jump_level
        
        continue
    
    # 더 이상 전파할 수 없을 때 랜덤값 대입
    if None in symbolic_exp.values():
        current_level += 1
        assignRandExp(symbolic_exp, levels, current_level, trail)
    else:
        isSatisfiable = True
        break;

print('===========최종 결과===========')
if isSatisfiable:
    print(symbolic_exp)
else:
    print("만족할 수 없는 수식")



