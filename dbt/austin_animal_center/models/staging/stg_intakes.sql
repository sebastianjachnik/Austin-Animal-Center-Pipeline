with source as (

    select * from {{ source('raw', 'raw_intakes') }}

),

renamed as (

    select
        -- identifiers
        cast(animal_id as string) as animal_id,
        cast(name as string) as name,

        -- timestamps
        cast(intake_datetime as timestamp) as intake_datetime,

        -- intake details
        cast(found_location as string) as found_location,
        cast(intake_type as string) as intake_type,
        cast(intake_condition as string) as intake_condition,

        -- animal attributes
        cast(animal_type as string) as animal_type,
        cast(sex_upon_intake as string) as sex_upon_intake,
        cast(age_upon_intake as string) as age_upon_intake,
        cast(breed as string) as breed,
        cast(color as string) as color

    from source

)

select * from renamed