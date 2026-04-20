with animal_stays as (

    select * from {{ ref('int_animal_stays') }}

),

final as (

    select
        -- identifiers
        animal_id,

        -- animal attributes
        animal_type,
        breed,
        color,

        -- intake details
        intake_datetime,
        intake_type,
        intake_condition,

        -- outcome details
        outcome_datetime,
        outcome_type,
        outcome_subtype,

        -- metrics
        timestamp_diff(outcome_datetime, intake_datetime, day) as stay_duration_days

    from animal_stays
    where intake_datetime is not null
      and outcome_datetime is not null
      and outcome_datetime >= intake_datetime

)

select * from final