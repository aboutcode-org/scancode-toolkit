

dependencies {
    runtimeOnly(group = "org.springframework", name = "spring-core", version = "2.5")
    runtimeOnly("org.springframework:spring-aop:2.5")
    runtimeOnly("org.hibernate:hibernate:3.0.5") {
        isTransitive = true
    }
    runtimeOnly(group = "org.hibernate", name = "hibernate", version = "3.0.5") {
        isTransitive = true
    }
}

