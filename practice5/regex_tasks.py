import re

# 1. 'a' + 0 или больше 'b'
print(bool(re.fullmatch(r"ab*", "abbb")))

# 2. 'a' + 2-3 'b'
print(bool(re.fullmatch(r"ab{2,3}", "abb")))

# 3. snake_case
text = "hello_world test_string"
print(re.findall(r"[a-z]+_[a-z]+", text))

# 4. Capital + lowercase
text = "Hello World Test"
print(re.findall(r"[A-Z][a-z]+", text))

# 5. a...b
print(bool(re.fullmatch(r"a.*b", "axxxb")))

# 6. replace space/comma/dot
text = "Hello, world. test"
print(re.sub(r"[ ,\.]", ":", text))

# 7. snake -> camel
def snake_to_camel(s):
    return re.sub(r"_([a-z])", lambda m: m.group(1).upper(), s)

print(snake_to_camel("hello_world_test"))

# 8. split by uppercase
text = "HelloWorldTest"
print(re.split(r"(?=[A-Z])", text))

# 9. insert spaces before capitals
print(re.sub(r"([A-Z])", r" \1", "HelloWorld"))

# 10. camel -> snake
def camel_to_snake(s):
    return re.sub(r"([A-Z])", r"_\1", s).lower()

print(camel_to_snake("HelloWorldTest"))