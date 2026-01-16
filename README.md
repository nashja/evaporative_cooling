# Notice

This is a work in progress.  Taking the blueprint (https://github.com/ludeeus/integration_blueprint) code for integration development
in home assistant and updating my custom code for calculating the effectiveness of an evaporative cooler given the external heat and
humidity environment.

## Why?

Evaporative cooling is really only effective in situations where the air his hot and dry outside, this integration calculates how
effective the cooling will be.

## What?

This integration just takes the input
data from user specified tempearture and humidity sensors (whether physical sensors, or weather sensors) and then using tables of
effective temperature for evaporative cooling displays the target potential temperature for an EC system.


## How?

Should be able to add this in HACS once it is working

## Next steps

Plans
-- only blueprint code in this repository currently
-- need to move current working EC code into this repository and in the style of the blueprint
-- consider adding an additional sensor which is an internal sensor to measure how well the EC is doing


