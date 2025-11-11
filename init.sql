CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nickname VARCHAR(32) UNIQUE NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    stack VARCHAR(32)[] CHECK (
        stack IS NULL OR (array_length(stack, 1) IS NOT NULL)
    )
);
