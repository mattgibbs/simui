from epics import ca

def batch_get(pv_list):
	chids = {}
	pvdata = {}
	for name in pv_list:
		chid = ca.create_channel(name, connect=False, auto_cb=False)
		chids[name] = chid
	for name, chid in chids.items():
		ca.connect_channel(chid)
	ca.poll()
	for name, chid in chids.items():
		ca.get(chid, wait=False)
	ca.poll()
	for name, chid in chids.items():
		val = ca.get_complete(chid)
		pvdata[name] = val
	return pvdata
