SELECT 
	'1',
	time
	FROM message
	INNER JOIN channel on channel.channel_id = message.channel_id 
	INNER JOIN category on channel.category_id = category.category_id
	INNER JOIN server on category.server_id = server.server_id
	WHERE 
		server.server_id = 679614550286663721 
		and category.category_id = 679614550286663722
		and message.time between '2020-04-07 14:50:32.072000UTC' AND '2020-04-07 18:39:01.384000UTC'
