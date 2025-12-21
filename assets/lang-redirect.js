  const names = {
    en:"English", bg:"Български", cs:"Čeština", da:"Dansk", de:"Deutsch", el:"Ελληνικά", es:"Español", et:"Eesti", fi:"Suomi", fr:"Français",
    ga:"Gaeilge", hr:"Hrvatski", hu:"Magyar", it:"Italiano", lt:"Lietuvių", lv:"Latviešu", mt:"Malti", nl:"Nederlands",
    pl:"Polski", pt:"Português", ro:"Română", sk:"Slovenčina", sl:"Slovenščina", sv:"Svenska"
  };
  const supported = Object.keys(names);
  const box = document.getElementById('langs');
  supported.sort().forEach(code => {
    const a = document.createElement('a');
    a.className='btn';
    a.href='/' + code + '/for-humans/';
    a.textContent = names[code] + ' (' + code + ')';
    box.appendChild(a);
  });

  // auto redirect (soft) – only if user is on root and no hash
  try {
    const pref = (navigator.language || 'en').toLowerCase().slice(0,2);
    if (supported.includes(pref)) {
      // do not hard redirect; just preselect top by moving it first (UX friendly)
      // Optional: uncomment next line for hard redirect
      // window.location.replace('/' + pref + '/for-humans/');
    }
  } catch(e){}
