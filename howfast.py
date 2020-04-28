import time
start = time.time()
count = 0
for i in range(10000):
    count += i**i % 210938141298
end = time.time()
print("time was: ", end-start)
