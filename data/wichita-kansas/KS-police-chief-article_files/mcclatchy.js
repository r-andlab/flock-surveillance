(function(w, d) {
	'use strict';
	var s1 = d.getElementsByTagName('script')[0],
		s = d.createElement('script'),
		onReady;

	s.src = '//tru.am/scripts/ta-pagesocial-sdk.js';

	onReady = function() {
		var l = document.location,
			h = l.hostname.toLowerCase(),
			cid;
		if (h.indexOf('miamiherald.com') > -1) {
			cid = '1736';
		} else if (h.indexOf('sacbee.com') > -1) {
			cid = '1812';
		} else if (h.indexOf('flkeysnews.com') > -1) {
			cid = '1808';
		} else if (h.indexOf('islandpacket.com') > -1) {
			cid = '1861';
		} else if (h.indexOf('tri-cityherald.com') > -1) {
			cid = '1852';
		} else if (h.indexOf('charlotteobserver.com') > -1) {
			cid = '1741';
		} else if (h.indexOf('modbee.com') > -1) {
			cid = '1742';
		} else if (h.indexOf('star-telegram.com') > -1) {
			cid = '1818';
		} else if (h.indexOf('kansascity.com') > -1) {
			cid = '1819';
		} else if (h.indexOf('newsobserver.com') > -1) {
			cid = '1827';
		} else if (h.indexOf('idahostatesman.com') > -1) {
			cid = '1835';
		} else if (h.indexOf('fresnobee.com') > -1) {
			cid = '1836';
		} else if (h.indexOf('kansas.com') > -1) {
			cid = '1839';
		} else if (h.indexOf('kentucky.com') > -1) {
			cid = '1840';
		} else if (h.indexOf('elnuevoherald.com') > -1) {
			cid = '1842';
		} else if (h.indexOf('thestate.com') > -1) {
			cid = '1843';
		} else if (h.indexOf('mahoningmatters.com') > -1) {
			cid = '1848';
		} else if (h.indexOf('bellinghamherald.com') > -1) {
			cid = '1849';
		} else if (h.indexOf('theolympian.com') > -1) {
			cid = '1851';
		} else if (h.indexOf('mercedsunstar.com') > -1) {
			cid = '1854';
		} else if (h.indexOf('sanluisobispo.com') > -1) {
			cid = '1855';
		} else if (h.indexOf('bnd.com') > -1) {
			cid = '1856';
		} else if (h.indexOf('sunherald.com') > -1) {
			cid = '1857';
		} else if (h.indexOf('ledger-enquirer.com') > -1) {
			cid = '1858';
		} else if (h.indexOf('macon.com') > -1) {
			cid = '1859';
		} else if (h.indexOf('bradenton.com') > -1) {
			cid = '1860';
		} else if (h.indexOf('myrtlebeachonline.com') > -1) {
			cid = '1863';
		} else if (h.indexOf('heraldonline.com') > -1) {
			cid = '1864';
		} else if (h.indexOf('heraldsun.com') > -1) {
			cid = '1865';
		} else if (h.indexOf('centredaily.com') > -1) {
			cid = '1866';
		} else if (h.indexOf('thenewstribune.com') > -1) {
			cid = '1833';
		} else if (h.indexOf('accesousa.com') > -1) {
			cid = '1946';
		} else if (h.indexOf('detourxp.com') > -1) {
			cid = '1965';
		} else if (h.indexOf('coralspringsflnews.com') > -1) {
			cid = '4330';
		} else if (h.indexOf('miramarflnews.com') > -1) {
			cid = '4329';
		} else if (h.indexOf('pembrokepinesflnews.com') > -1) {
			cid = '4328';
		}

		if (cid) {
			w.TRUE_ANTHEM.configure(cid);
		}
	};
	if (s.addEventListener) {
		s.addEventListener('load', onReady, false);
	} else {
		s.onreadystatechange = function() {
			if (s.readyState in {
					loaded: 1,
					complete: 1
				}) {
				s.onreadystatechange = null;
				onReady();
			}
		};
	}
	s1.parentNode.insertBefore(s, s1);
}(window, document));