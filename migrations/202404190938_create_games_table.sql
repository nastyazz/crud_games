-- migrate:up

create extension if not exists "uuid-ossp";

create schema games_data;


create table games_data.games
(
    id         uuid primary key default uuid_generate_v4(),
    title text,
    genre  text,
    price float
);

create table games_data.comment
(
    id          uuid primary key default uuid_generate_v4(),
    description_       text,
    date_public date,
    estimation float,
    game_id uuid references games_data.games not null
);


create table games_data.buyer
(
    id          uuid primary key default uuid_generate_v4(),
    nickname       text,
    date_registrate date
);

create table games_data.games_to_buyer
(
    games_id uuid references games_data.games,
    buyer_id  uuid references games_data.buyer,
    primary key (games_id, buyer_id)
);

-- migrate:down