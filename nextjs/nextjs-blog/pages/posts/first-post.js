import Image from 'next/image';
import Head from 'next/head';
import Link from 'next/link'
import Layout from '../../components/layout';

export default function FirstPost() {
    return (
    <Layout>
        <Head>
          <title>First Post</title>
        </Head>
        <h1>First Post</h1>
        <Image 
        src="/images/profile.jpg"
        alt="Your Name"
        height={144} 
        width={144}
        />
        <h2>
          <Link href="/">← Back to home</Link>
        </h2>
      </Layout>
    );
  }