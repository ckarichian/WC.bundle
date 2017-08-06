NAME = 'Watch Cartoon'
BASE_URL = 'http://www.watchcartoononline.com'
ascii_uppercase = list('#ABCDEFGHIJKLMNOPQRSTUVWXYZ')

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36'

###################################################################################################
@handler('/video/watchcartoon', NAME, thumb='watchcartoon.jpg')
def MainMenu():

	oc = ObjectContainer(title1='Watch Cartoons', title2='Select the first letter of the show', art=R('theatre.jpg'))
	
	oc.add(InputDirectoryObject(key = Callback(SearchSections, title="Search"), title = "Search"))
	
	for c in ascii_uppercase:	
		oc.add(
			DirectoryObject(
				key = Callback(Category, letter=c, index=(ascii_uppercase.index(c)+1)),
				title = c
			)
		)

	return oc
	
###################################################################################################
@route('/video/watchcartoon/category')
def Category(letter, index):

	two = 'Letter %s' % letter
	oc = ObjectContainer(title1=NAME, title2=two, art=R('theatre.jpg'))
	
	shows = HTML.ElementFromURL('%s/cartoon-list' % (BASE_URL), cacheTime = CACHE_1HOUR).xpath('//*[@id="ddmcc_container"]/div[1]/ul/ul[%s]/li' % index)
	
	for show in shows:
		
		try:
			title = show.xpath('./a/text()')
			href = show.xpath('./a')[0].get('href')
			tit = ''.join(title)
			
			oc.add(
				TVShowObject(
					key = Callback(Show, title=tit, path=href),
					rating_key = 'watch-%s' % href,
					title = tit
				)
			)		
		except IndexError:
			href = 1
	

	return oc

####################################################################################################
@route('/video/watchcartoon/show')
def Show(title, path):
	
	oc = ObjectContainer(title1=NAME, title2=title)	
	
	page = HTML.ElementFromURL(path)	
	episodes = page.xpath('//*[@id="sidebar_right3"]/div')
	thumb = page.xpath('//*[@id="sidebar_cat"]/img/@src')[0]
	
	
	
	for episode in episodes:
		epTitle = episode.xpath('./a/text()')[0]
		href = episode.xpath('./a/@href')[0]
			
		oc.add(
			EpisodeObject(
				url = href,
				title = epTitle.replace(title,''),
				show = title,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb)
			)
		)	
	
	if len(oc) < 1:
		return ObjectContainer(header="Empty", message="This season doesn't contain any episodes.")
	else:
		Log("############## Completed")
		oc.objects.sort(key = lambda obj: obj.index)
		return oc

####################################################################################################
@route('/video/watchcartoon/search')
def SearchSections(title, query):
	oc = ObjectContainer(title2=title)
	letters = HTML.ElementFromURL('%s/cartoon-list' % (BASE_URL)).xpath('//*[@id="ddmcc_container"]/div/ul/ul')
	
	for letter in letters:
		shows = letter.xpath('./li')
		for show in shows:
			try: matchShow = query in show.xpath('./a/text()')[0].lower()
			except: continue
			if matchShow:
				try:
					title = show.xpath('./a/text()')[0]
					href = show.xpath('./a')[0].get('href')
					#tit = ''.join(title)
					
					oc.add(
						TVShowObject(
							key = Callback(Show, title=title, path=href),
							rating_key = 'watch-%s' % href,
							title = title
						)
					)		
				except IndexError:
					href = 1
			matchShow = False
	
	if len(oc) < 1:
		return ObjectContainer(header="No Results", message="No results found")
	else:
		return oc