def messageChunks(string, chunk_length):
	if(len(string) <= chunk_length):
		return [string]
	
	parse = string
	chunks = []
	potential_chunks_number = len(parse) // chunk_length
	while potential_chunks_number > 0:
		shift = 0
		start = 0
		end = 0
		for chunk in range(1, potential_chunks_number + 1):
			i = (chunk_length * chunk - 1) - shift
			while(parse[i] != ' ' and parse[i] != '\n'):
				i = i - 1
				shift = shift + 1
			end = i
			chunks.append(parse[start:end])
			start = end + 1
		parse = parse[start:]
		#print(parse, "len:", len(parse))
		potential_chunks_number = len(parse) // chunk_length
	if len(parse) > 0:
		chunks.append(parse)
	return chunks


def fileChunks(data, chunk_length):

	chunks = []
	complete_chunk_amount = len(data) // chunk_length 
	for i in range(complete_chunk_amount):
		chunks.append(data[i * chunk_length: chunk_length * (i + 1)])
	
	last_chunk = data[chunk_length * complete_chunk_amount:]
	if len(last_chunk) > 0:
		chunks.append(last_chunk)
	
	return chunks
	


