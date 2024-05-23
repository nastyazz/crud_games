-- migrate:up

insert into games_data.games(title, genre, price)
select md5(random()::text),
        md5(random()::text),
        generate_series(0, 3000);


insert into games_data.buyer(nickname, date_registrate)
select md5(random():: text),
        now() - (random() * (interval '90 days'));


insert into games_data.games_to_buyer(games_id, buyer_id)
select games.id, buyer.id
from games_data.games
cross join lateral (
    select id from games_data.buyer
    order by random()
    limit 1
) buyer;

insert into games_data.comment(description_, date_public, estimation, game_id) 
select md5(random():: text),
    now() - (random() * (interval '90 days')),
    generate_series(0, 5),
            g.id
from 
    generate_series(1, 10) as comment(id)  
cross join                                                                      
    (select id from games_data.games order by random() LIMIT 100) as g;;

-- migrate:down