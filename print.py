for i in range(0,47):
    print(f'CHARIZARD_{i} = pygame.image.load("asset/Charizard/charizardframe_{i}.png")')
    print(f'CHARIZARD_{i} = pygame.transform.scale(CHARIZARD_{i}, (300, 300))')

print("list_char = [", end="")
for i in range(0, 47):
    if i < 46:
        print(f"CHARIZARD_{i}, ", end="")
    else:
        print(f"CHARIZARD_{i}", end="")
print("]")