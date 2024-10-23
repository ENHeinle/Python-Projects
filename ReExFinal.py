
file = open('Sum-Actual.txt', 'r')
sum = 0
import re
for line in file:
    numbers = re.findall('[0-9]+', line)
    if not numbers:
        continue
    else:
        for number in numbers:
            sum += int(number)

print(sum)