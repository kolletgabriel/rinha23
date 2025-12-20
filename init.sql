CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nickname VARCHAR(32) UNIQUE NOT NULL,
    fullname VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    stack VARCHAR(32)[]
);

CREATE FUNCTION concat_cols(
    str1 VARCHAR(32),
    str2 VARCHAR(100),
    arr VARCHAR(32)[]
) RETURNS VARCHAR IMMUTABLE AS $$
    SELECT (
        str1 || ' ' || str2 || ' ' || array_to_string(
            coalesce(arr, '{}'::VARCHAR[]), ' '
        )
    )
$$ LANGUAGE SQL;

CREATE EXTENSION pg_trgm;
CREATE INDEX idx_trgm_users_search ON users USING GIST (
    concat_cols(nickname, fullname, stack)
    gist_trgm_ops
);
