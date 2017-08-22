#from idoc.models import Document, IDocument
#from idoc.models import DownloadHistory, IDocDownload
#from idoc.models import DocumentRating, IDocRating
#
#def migrate_downloads():
#	for dl in DownloadHistory.objects.all():
#		if dl.document.idocument_set.all():
#			newdoc = dl.document.idocument_set.all()[0]
#			idl = IDocDownload(
#					downloader = dl.downloader,
#					document = newdoc,
#					time_stamp = dl.time_stamp
#				  )
#			idl.save()
#
#def migrate_ratings():
#	for dr in DocumentRating.objects.all():
#		if dr.document.idocument_set.all():
#			newdoc = dr.document.idocument_set.all()[0]
#			idr = IDocRating(
#					rater = dr.rater,
#					rating = dr.rating,
#					document = newdoc,
#					time_stamp = dr.time_stamp
#				  )
#			idr.save()
#
#def migrate_documents():
#	for doc in Document.objects.all():
#		idoc = IDocument(
#				creator = doc.owner,
#				time_stamp = doc.creation_time,
#				mp_code = "DO",
#				title = doc.title,
#				details = doc.description,
#				anonymous = doc.anonymous,
#				tags = doc.tags,
#				sharing = doc.sharing,
#				thumb_up = doc.thumb_up,
#				thumb_down = doc.thumb_down,
#				thumbs = doc.thumbs,
#				visits = doc.visits,
#				deleted = doc.deleted,
#				olddoc = doc,
#				doctype = doc.doctype,
#				file = doc.file,
#				version = "1.0",
#				downloads = doc.downloads,
#				freedownloads = doc.downloads,
#				rating = doc.rating_float()
#			 )
#		idoc.save()
#

