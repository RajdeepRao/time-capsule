resource "aws_s3_bucket" "media_bucket" {
    bucket = "time-capsule-media"
}

resource "aws_s3_bucket_acl" "media_bucket_acl" {
  bucket = aws_s3_bucket.media_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_policy" "allow_access_to_cloudfront" {
  bucket = aws_s3_bucket.media_bucket.id
  policy = data.aws_iam_policy_document.allow_access_to_cloudfront.json
}

data "aws_iam_policy_document" "allow_access_to_cloudfront" {
  statement {
    sid = "ToAllowAccessToCloudFront"
    
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }

    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]

    resources = [
      aws_s3_bucket.media_bucket.arn,
      "${aws_s3_bucket.media_bucket.arn}/*",
    ]
  }
}