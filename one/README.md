* Name : Wai Han
* Challenge One

---


# Exploration

* Assets inside the repo
    * Dockerfile, docker-compose.yml, nginx.conf.
    * html.tgz -> unpacked into /var/www in container.

* Maps port 8081:8080
* Adds html.tgz to /var/www
* Copies custom nginx.conf
* Serves from /var/www/html (root directory)
* Listens on port 8080
* Has autoindex enabled **
* Custom logging format with timing info

** indicates the initial guess for an opportunity to find the flag.

---

## Understanding `nginx.conf`

`nginx.conf` is the main configuration file for Nginx, a high-performance web server and reverse proxy. It controls how Nginx behaves.

```nginx
# Example File
user  nginx;
worker_processes  auto;

# Logging
error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

# Events block
events {
    worker_connections 1024;
}

# HTTP block
http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    # Server block
    server {
        listen       80;
        server_name  example.com;

        location / {
            root   /usr/share/nginx/html;
            index  index.html index.htm;
        }
    }
}
```

---

## What's html.tgz file?

It's a compressed archive (tar + gzip) containing a directory of HTML files (and possibly CSS, JS, etc.).

In our case:
```css
html/
  index.html
  img/
```

So, essentially, this is a compressed file of a website.

---

## Initial Understanding

- This is a custom Nginx container (default is overriden by `nginx.conf` file).
- Serves content from a directory that was archived into `html.tgz`?
- My guess is that there might be something wrong / vulnerable in the `nginx.conf` file since it is a configuration file that sets the nginx server. 
- I asked GPT4.0 to analyze the `nginx.conf` file and `autoindex on` seems to be the major issue.
    *  `autoindex on`; — Directory Listing Enabled
    * What it does: Automatically generates and displays an index of files in a directory if no index file is present.
    * Why it’s risky: Exposes sensitive files or directory structure (e.g., .env, config.yaml, backups).

--- 

## Action Plan 

1. Run the Docker Container                             (OK)
2. Access the web service on port 8081                  (OK)
3. Check for directory listings (autoindex)             (Just get index.html; com.png gives 403).
4. Examine container contents                           (OK; go to container bash and find the files for a potential flag)
5. Look for hidden files/directories                    (OK)
6. Check logs for sensitive data                        (OK)
7. Check for common CTF hiding spots                    (OK)
8. Check for exposed .git/ → dump repo history          (Solution Found)
    Find flag across commits / hidden files

<small>"OK" here just means that I did it but didn't end up being very useful in the final exploit (at least not directly).</small>

---

## Trying to find Solution

1. curl http://localhost:8081/ just gives index.html file. Couldn't find the flag here.
2. curl http://localhost:8081/img/ returns
```
<html>
<head><title>Index of /img/</title></head>
<body>
<h1>Index of /img/</h1><hr><pre><a href="../">../</a>
<a href="com.png">com.png</a>                                            21-Oct-2022 05:17               27052
<a href="door.png">door.png</a>                                           21-Oct-2022 13:36               75852
</pre><hr></body>
</html>
```

3. `com.png` file is never used in the `index.html` file. It's suspicious and the solution might be in there. When I try `curl http://localhost:8081/img/com.png`, I get 403 Forbidden.

4. Try using exiftool in case there's a flag in the metadata.

```
ExifTool Version Number         : 13.30
File Name                       : com.png
Directory                       : .
File Size                       : 27 kB
File Modification Date/Time     : 2022:10:20 22:17:34-07:00
File Access Date/Time           : 2025:06:26 16:08:37-07:00
File Inode Change Date/Time     : 2025:06:26 15:31:16-07:00
File Permissions                : -rw-------
File Type                       : PNG
File Type Extension             : png
MIME Type                       : image/png
Image Width                     : 1920
Image Height                    : 1080
Bit Depth                       : 8
Color Type                      : RGB with Alpha
Compression                     : Deflate/Inflate
Filter                          : Adaptive
Interlace                       : Noninterlaced
Pixels Per Unit X               : 2834
Pixels Per Unit Y               : 2834
Pixel Units                     : meters
Image Size                      : 1920x1080
Megapixels                      : 2.1
```

5. Also notice that .git is exposed 

6. Download the repo: `git-dumper http://localhost:8081/.git/ dumped_repo/`. 

7. `com.png` is again not in the git repo. Manually placed after? 

8. Ok. Goes through the previous commits of the .git that I just downloaded. Finally found the flag! `git show $(cat .git/ORIG_HEAD)`.

```
commit 4ba53800ea4f1f8e433e16c5c37a2be52a961838
Author: Holland Wan <noreply@noreply.com>
Date:   Fri Oct 21 22:47:51 2022 +0800

    What is this?

diff --git a/flag.txt b/flag.txt
new file mode 100644
index 0000000..54c849b
--- /dev/null
+++ b/flag.txt
@@ -0,0 +1 @@
+hkcert22{n0stalgic_w3bs1t3_br1ings_m3_b4ck_to_2000}
diff --git a/index.html b/index.html
deleted file mode 100644
index 98fa7c2..0000000
--- a/index.html
+++ /dev/null
```


## Takeaway

Revise: The exposed `.git` led us to recover the entire repository history and find the flag in a previous commit.

Lesson: The `com.png` with 403 permission was probably a red herring and I got distracted. I should have checked the git logs first.

## Exploit / Solution

```
git show $(cat .git/ORIG_HEAD)
```

## Flag

```
hkcert22{n0stalgic_w3bs1t3_br1ings_m3_b4ck_to_2000}
```

## Lessons Learned

* Remove `.git` folder from the container image
* `autoindex off`
* Don't commit secrets to git. Use `.env`, `.gitignore`
