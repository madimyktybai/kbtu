#1
# def squares_up_to_n(n):
#     for i in range(n):
#         yield i ** 2

# n = 5
# for sq in squares_up_to_n(n):
#     print(sq)


#2
# def even_generator(n):
#     for i in range(n + 1):
#         if i % 2 == 0:
#             yield str(i)

# n = int(input())
# gen = even_generator(n)

# print(", ".join(gen))


#3
# def divisible_by_3_and_4(n):
#     for i in range(n + 1):
#         if i % 3 == 0 and i % 4 == 0:
#             yield i

# for num in divisible_by_3_and_4(50):
#     print(num)


#4
# def squares(a, b):
#     for i in range(a, b+1):
#         yield i ** 2

# start, end = 3, 7
# for val in squares(start, end):
#     print(val)


#5
# def countdown(n):
#     while n >= 0:
#         yield n
#         n -= 1

# for x in countdown(5):
#     print(x) # Выведет 5, 4, 3, 2, 1, 0