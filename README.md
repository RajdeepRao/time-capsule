# Time-Capsule

A google photos of sorts, but free (Or with min infra costs)
The main aim is to build a light web UI over s3 to be able to browse and store media content that would otherwise blow through the tiers on google storage.

Thinking of it as a 2 parter
1. All the infra in terraform
2. ~NextJS app for the FE to render some of these images/videos and such~
2. Wrote this in a flask app with JINJA templates for FE

Nice to haves
- Generate thumbnails 
- Upload from the UI
- WAF so that everyone can't access the Cloudfront URL
- Auth so folks can have their own area in S3 to store stuff
