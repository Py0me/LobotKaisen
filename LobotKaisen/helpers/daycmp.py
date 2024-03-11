from time import struct_time

def same_day(first_time: struct_time, second_time: struct_time) -> bool:
	return (
		first_time.tm_year == second_time.tm_year and
		first_time.tm_yday == second_time.tm_yday
	)

def same_minute(first_time: struct_time, second_time: struct_time) -> bool:
	return (
		first_time.tm_year == second_time.tm_year and
		first_time.tm_yday == second_time.tm_yday and
		first_time.tm_min  == second_time.tm_min
	)