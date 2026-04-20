with source as (

    select * from {{ source('raw', 'raw_outcomes') }}

),

renamed as (

    select
        -- identifiers
        cast(animal_id as string) as animal_id,
        cast(name as string) as name,

        -- timestamps
        cast(date_of_birth as date) as date_of_birth,
        cast(outcome_datetime as timestamp) as outcome_datetime,

        -- outcome details
        cast(outcome_type as string) as outcome_type,
        cast(outcome_subtype as string) as outcome_subtype,

        -- animal attributes
        cast(animal_type as string) as animal_type,
        cast(sex_upon_outcome as string) as sex_upon_outcome,
        cast(age_upon_outcome as string) as age_upon_outcome,
        cast(breed as string) as breed,
        cast(color as string) as color

    from source

)

select * from renamed