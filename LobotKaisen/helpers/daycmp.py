from time import gmtime

def same_day(first_time: float, second_time: float) -> bool:
	first_time = gmtime(first_time)
	second_time = gmtime(second_time)
	return (
		first_time.tm_year == second_time.tm_year and
		first_time.tm_yday == second_time.tm_yday
	)

def same_minute(first_time: float, second_time: float) -> bool:
	first_time = gmtime(first_time)
	second_time = gmtime(second_time)
	return (
		first_time.tm_year == second_time.tm_year and
		first_time.tm_yday == second_time.tm_yday and
		first_time.tm_min  == second_time.tm_min
	)