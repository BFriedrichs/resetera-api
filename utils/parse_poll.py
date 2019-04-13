
def parse_poll(cont):
    header = cont.find(class_='block-header').get_text(strip=True)
    total_votes = int(cont.find('dd').get_text(strip=True).replace(',', ''))
    results = []

    result_nodes = cont.find_all(class_='pollResult')
    for r in result_nodes:
        name = r.find(class_='pollResult-response').get_text(strip=True)
        votes = r.find(class_='pollResult-votes').get_text(strip=True)
        percentage = r.find(class_='pollResult-percentage').get_text(strip=True)
        results.append({
            'name': name,
            'votes': int(votes.split(":")[-1].replace(',', '')),
            'percentage': float(percentage.replace("%", ""))
        })

    return {
        'title': header,
        'total_votes': total_votes,
        'results': results
    }