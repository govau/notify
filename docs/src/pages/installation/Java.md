If you are using Gradle:

```groovy
repositories {
    jcenter()
}
...
compile 'au.gov.notify:notify-client-java:4.0.0-RELEASE'
```

If you are using Maven:

```xml
<repositories>
  <repository>
    <id>central</id>
    <name>bintray</name>
    <url>http://jcenter.bintray.com</url>
  </repository>
</repositories>
...
<dependency>
  <groupId>au.gov.notify</groupId>
  <artifactId>notify-client-java</artifactId>
  <version>4.0.0-RELEASE</version>
  <type>pom</type>
</dependency>
```
