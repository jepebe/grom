# GROM

Statically duck typed

## Expressions

```
34 + 35
500 - 80

```



## Language

```
include "io"

fun sum(u64 a, u64 b) -> u64:
    <- a + b
end

fun main():
    u64 s <- sum(34, 45)
    print(s)
end
```