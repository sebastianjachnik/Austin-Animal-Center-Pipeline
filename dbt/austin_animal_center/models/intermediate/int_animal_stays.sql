with intakes as (

    select * from {{ ref('stg_intakes') }}

),

outcomes as (

    select * from {{ ref('stg_outcomes') }}

)

select
    -- identifiers
    i.animal_id,

    -- animal attributes (von intake genommen)
    i.animal_type,
    i.breed,
    i.color,

    -- intake info
    i.intake_datetime,
    i.intake_type,
    i.intake_condition,

    -- outcome info
    o.outcome_datetime,
    o.outcome_type,
    o.outcome_subtype

from intakes i
left join outcomes o
    on i.animal_id = o.animal_id