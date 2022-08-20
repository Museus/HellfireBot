heats = {}

for i in range(5):
    heats[f'HL{i + 1}'] = 1
for i in range(4):
    heats[f'LC{i + 1}'] = 1
for i in range(2):
    heats[f'CF{i + 1}'] = 1
for i in range(3):
    heats[f'JS{i + 1}'] = 1
for i in range(4):
    heats[f'EM{i + 1}'] = i + 1
for i in range(2):
    heats[f'CP{i + 1}'] = 1
for i in range(2):
    heats[f'BP{i + 1}'] = i + 2