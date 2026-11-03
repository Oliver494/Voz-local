import {cpSync, mkdirSync, copyFileSync, rmSync} from 'node:fs';
rmSync('desktop-dist', {recursive:true, force:true});
mkdirSync('desktop-dist', {recursive:true});
cpSync('static', 'desktop-dist/static', {recursive:true});
copyFileSync('static/index.html', 'desktop-dist/index.html');
