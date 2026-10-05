# Java Label Samples

Reviewing label noise: True SZZ can erroneously label refactoring or style changes as bugs if keywords match.

### Buggy: 0 (Commit: f29de38d1f3a7fcea750c79977649cde99d7e8d1)
**Repo**: junit5
```java
@Test
		void valueFromParentCanBeOverriddenInChild() {
			parentStore.put(namespace, key, value);

			Object otherValue = new Object();
			store.put(namespace, key, otherValue);
			assertEquals(otherValue, store.get(namespace, key));

			assertEquals(value, parentStore.get(namespace, key));
		}
```

### Buggy: 1 (Commit: 5a29b8780f1f18b527e102c4126da7abc0abaca1)
**Repo**: junit5
```java
static void assertSame(@Nullable Object expected, @Nullable Object actual, @Nullable String message) {
		if (expected != actual) {
			failNotSame(expected, actual, message);
		}
	}
```

### Buggy: 1 (Commit: 25c489a9babe1e08b76dd2a10b6d3609b0d34f39)
**Repo**: lucene
```java
public long ramBytesUsed() {
    return deletedDocs.ramBytesUsed();
  }
```

### Buggy: 1 (Commit: 5c9d8ca5fe6b9a9e200a459d479f5ea636c20050)
**Repo**: kafka
```java
@Test
    public void testRecoverWithEmptyActiveSegment() throws IOException {
        int numMessages = 100;
        int messageSize = 100;
        int segmentSize = 7 * messageSize;
        int indexInterval = 3 * messageSize;
        LogConfig logConfig = new LogTestUtils.LogConfigBuilder()
                .segmentBytes(segmentSize)
                .indexIntervalBytes(indexInterval)
                .segmentIndexBytes(4096)
                .build();
        UnifiedLog log = createLog(logDir, logConfig);
        for (int i = 0; i < numMessages; i++) {
            log.appendAsLeader(LogTestUtils.singletonRecords(TestUtils.randomBytes(messageSize), mockTime.milliseconds() + i * 10), 0);
        }
        assertEquals(numMessages, log.logEndOffset(),
                "After appending " + numMessages + " messages to an empty log, the log end offset should be " + numMessages);
        log.roll();
        log.flush(false);
        assertThrows(NoSuchFileException.class, () -> log.activeSegment().sanityCheck(true));
        long lastOffset = log.logEndOffset();
        log.closeHandlers();

        UnifiedLog log2 = createLog(logDir, logConfig, lastOffset, false);
        assertEquals(lastOffset, log2.recoveryPoint(), "Unexpected recovery point");
        assertEquals(numMessages, log2.logEndOffset(), "Should have " + numMessages + " messages when log is reopened w/o recovery");
        assertEquals(0, log2.activeSegment().timeIndex().entries(), "Should have same number of time index entries as before.");
        log2.activeSegment().sanityCheck(true); // this should not throw because the LogLoader created the empty active log index file during recovery

        for (int i = 0; i < numMessages; i++) {
            log2.appendAsLeader(LogTestUtils.singletonRecords(TestUtils.randomBytes(messageSize), mockTime.milliseconds() + i * 10), 0);
        }
        log2.roll();
        assertThrows(NoSuchFileException.class, () -> log2.activeSegment().sanityCheck(true));
        log2.flush(true);
        log2.activeSegment().sanityCheck(true); // this should not throw because we flushed the active segment which created the empty log index file
        lastOffset = log2.logEndOffset();

        UnifiedLog log3 = createLog(logDir, logConfig, lastOffset, false);
        assertEquals(lastOffset, log3.recoveryPoint(), "Unexpected recovery point");
        assertEquals(2 * numMessages, log3.logEndOffset(), "Should have " + numMessages + " messages when log is reopened w/o recovery");
        assertEquals(0, log3.activeSegment().timeIndex().entries(), "Should have same number of time index entries as before.");
        log3.activeSegment().sanityCheck(true); // this should not throw

        log3.close();
    }
```

### Buggy: 1 (Commit: 5a29b8780f1f18b527e102c4126da7abc0abaca1)
**Repo**: junit5
```java
public @Nullable TestSource findTestSource(Description description) {
		TestSource testSource = testSourceCache.computeIfAbsent(description, this::computeTestSource);
		return testSource == NULL_SOURCE ? null : testSource;
	}
```

### Buggy: 1 (Commit: 5a29b8780f1f18b527e102c4126da7abc0abaca1)
**Repo**: junit5
```java
private void walk(@Nullable TestDescriptor globalLockDescriptor, TestDescriptor testDescriptor,
			NodeExecutionAdvisor advisor) {

		if (globalLockDescriptor != null && advisor.getResourceLock(globalLockDescriptor) == globalReadWriteLock) {
			// Global read-write lock is already being enforced, so no additional locks are needed
			return;
		}

		Set<ExclusiveResource> exclusiveResources = getExclusiveResources(testDescriptor);
		if (exclusiveResources.isEmpty()) {
			if (globalLockDescriptor != null && globalLockDescriptor.equals(testDescriptor)) {
				advisor.useResourceLock(globalLockDescriptor, globalReadLock);
			}
			testDescriptor.getChildren().forEach(child -> {
				var newGlobalLockDescriptor = globalLockDescriptor == null //
						? nullUnlessRequiresGlobalReadLock(child) //
						: globalLockDescriptor;
				walk(newGlobalLockDescriptor, child, advisor);
			});
		}
		else {
			Preconditions.notNull(globalLockDescriptor,
				() -> "Node requiring exclusive resources must also require global read lock: " + testDescriptor);

			Set<ExclusiveResource> allResources = new HashSet<>(exclusiveResources);
			if (isReadOnly(allResources)) {
				doForChildrenRecursively(testDescriptor, child -> allResources.addAll(getExclusiveResources(child)));
				if (!isReadOnly(allResources)) {
					forceDescendantExecutionModeRecursively(advisor, testDescriptor);
				}
			}
			else {
				advisor.forceDescendantExecutionMode(testDescriptor, SAME_THREAD);
				doForChildrenRecursively(testDescriptor, child -> {
					allResources.addAll(getExclusiveResources(child));
					advisor.forceDescendantExecutionMode(child, SAME_THREAD);
				});
			}
			if (allResources.contains(GLOBAL_READ_WRITE)) {
				advisor.forceDescendantExecutionMode(globalLockDescriptor, SAME_THREAD);
				doForChildrenRecursively(globalLockDescriptor, child -> {
					advisor.forceDescendantExecutionMode(child, SAME_THREAD);
					// Remove any locks that may have been set for siblings or their descendants
					advisor.removeResourceLock(child);
				});
				advisor.useResourceLock(globalLockDescriptor, globalReadWriteLock);
			}
			else {
				if (globalLockDescriptor.equals(testDescriptor)) {
					allResources.add(GLOBAL_READ);
				}
				else {
					allResources.remove(GLOBAL_READ);
				}
				advisor.useResourceLock(testDescriptor, lockManager.getLockForResources(allResources));
			}
		}
	}
```

### Buggy: 0 (Commit: 9a3cd2b4e7d327b1c1190099f5edc20e537d21db)
**Repo**: spring-boot
```java
@Test
	void routerFunctionShouldHaveOrderZero() {
		this.contextRunner.withUserConfiguration(CustomRouterFunctions.class).run((context) -> {
			Map<String, ?> beans = context.getBeansOfType(RouterFunction.class);
			Object[] ordered = context.getBeanProvider(RouterFunction.class).orderedStream().toArray();
			assertThat(beans.get("before")).isSameAs(ordered[0]);
			assertThat(beans.get("graphQlRouterFunction")).isSameAs(ordered[1]);
			assertThat(beans.get("after")).isSameAs(ordered[2]);
		});
	}
```

### Buggy: 1 (Commit: 8ba2020a55e07ea875ab142d7a0bf77acb310992)
**Repo**: elasticsearch
```java
protected static void addTestCaseSuppliers(
        List<TestCaseSupplier> suppliers,
        DataType[] dataTypes,
        DataType gridType,
        TriFunction<BytesRef, Integer, Consumer<String>, Object> expectedValue,
        QuadFunction<BytesRef, Integer, GeoBoundingBox, Consumer<String>, Object> expectedValueWithBounds
    ) {
        for (DataType spatialType : dataTypes) {
            TestCaseSupplier.TypedDataSupplier geometrySupplier = testCaseSupplier(spatialType, false);
            // Limit precision for geo_shape to avoid generating millions of cells for complex geometries
            int maxPrecision = spatialType == GEO_SHAPE ? 4 : 8;
            for (boolean literalPrecision : List.of(true)) {
                // TODO: add 'false' case once we support non-literal precision
                String testName = spatialType.typeName() + (literalPrecision ? " with literal precision" : " with precision");
                suppliers.add(new TestCaseSupplier(testName, List.of(spatialType, INTEGER), () -> {
                    TestCaseSupplier.TypedData geoTypedData = geometrySupplier.get();
                    BytesRef geometry = (BytesRef) geoTypedData.data();
                    int precision = between(1, maxPrecision);
                    TestCaseSupplier.TypedData precisionData = new TestCaseSupplier.TypedData(precision, INTEGER, "precision");
                    String evaluatorName = "FromFieldAndLiteralEvaluator[in=Attribute[channel=0], precision=Attribute[channel=1]";
                    if (literalPrecision) {
                        precisionData = precisionData.forceLiteral();
                        evaluatorName = "FromFieldAndLiteralEvaluator[wkbBlock=Attribute[channel=0], precision=" + precision + "]";
                    }
                    List<String> warnings = new ArrayList<>();
                    Object expected = expectedValue.apply(geometry, precision, warnings::add);
                    TestCaseSupplier.TestCase tc = new TestCaseSupplier.TestCase(
                        List.of(geoTypedData, precisionData),
                        getFunctionClassName() + evaluatorName,
                        gridType,
                        equalTo(expected)
                    );
                    if (warnings.isEmpty() == false) {
                        tc = tc.withWarning("Line 1:1 [source]: " + warnings.get(0));
                    }
                    return tc;
                }));
                // Test with bounds
                String boundsTestName = testName + " and bounds";
                suppliers.add(new TestCaseSupplier(boundsTestName, List.of(spatialType, INTEGER, GEO_SHAPE), () -> {
                    TestCaseSupplier.TypedData geoTypedData = geometrySupplier.get();
                    BytesRef geometry = (BytesRef) geoTypedData.data();
                    int precision = between(1, maxPrecision);
                    TestCaseSupplier.TypedData precisionData = new TestCaseSupplier.TypedData(precision, INTEGER, "precision");
                    String evaluatorName = "FromFieldAndLiteralAndLiteralEvaluator[in=Attribute[channel=0], bounds=[";
                    if (literalPrecision) {
                        precisionData = precisionData.forceLiteral();
                        evaluatorName = "FromFieldAndLiteralAndLiteralEvaluator[in=Attribute[channel=0]";
                    }
                    var boundsData = randomBoundsData();
                    List<String> warnings = new ArrayList<>();
                    Object boundedExpected = expectedValueWithBounds.apply(geometry, precision, boundsData.geoBoundingBox(), warnings::add);
                    TestCaseSupplier.TestCase tc = new TestCaseSupplier.TestCase(
                        List.of(geoTypedData, precisionData, boundsData.typedData),
                        startsWith(getFunctionClassName() + evaluatorName),
                        gridType,
                        equalTo(boundedExpected)
                    );
                    if (warnings.isEmpty() == false) {
                        tc = tc.withWarning("Line 1:1 [source]: " + warnings.get(0));
                    }
                    return tc;
                }));
            }
        }
    }
```

### Buggy: 1 (Commit: a0f0cf00b347297d2eff3f46c66f3f90b0c36e49)
**Repo**: spring-boot
```java
@Test
	void getLayerWhenFileHasSpaceReturnsLayer() throws Exception {
		IndexedLayers layers = new IndexedLayers(getIndex(), "BOOT-INF/classes");
		assertThat(layers.getLayer(mockEntry("a b/c d"))).isEqualTo("application");
	}
```

### Buggy: 1 (Commit: e1ce120c6a60df8fe1bf37b78127eea7562662e4)
**Repo**: commons-lang
```java
private static String typeVariableToString(final TypeVariable<?> typeVariable) {
        final StringBuilder builder = new StringBuilder(typeVariable.getName());
        final Type[] bounds = typeVariable.getBounds();
        if (bounds.length > 0 && !(bounds.length == 1 && Object.class.equals(bounds[0]))) {
            // https://issues.apache.org/jira/projects/LANG/issues/LANG-1698
            // There must be a better way to avoid a stack overflow on Java 17 and up.
            // Bounds are different in Java 17 and up where instead of Object you can get an interface like Comparable.
            final Type bound = bounds[0];
            boolean append = true;
            if (bound instanceof ParameterizedType) {
                final Type rawType = ((ParameterizedType) bound).getRawType();
                if (rawType instanceof Class && ((Class<?>) rawType).isInterface()) {
                    // Avoid recursion and stack overflow on Java 17 and up.
                    append = false;
                }
            }
            if (append) {
                builder.append(" extends ");
                AMP_JOINER.join(builder, bounds);
            }
        }
        return builder.toString();
    }
```

### Buggy: 1 (Commit: 009666592edfc975e07a683ad5680c17a59d8ba7)
**Repo**: elasticsearch
```java
public void testBuildModelFromConfigAndSecrets_ChatCompletion() throws IOException {
        var model = createTestModel(TaskType.CHAT_COMPLETION);
        validateModelBuilding(model);
    }
```

### Buggy: 1 (Commit: d000e630775cfa45752eeb491a197283e7370621)
**Repo**: mockito
```java
@Override
        Class<?> injectionBase(ClassLoader classLoader, String typeName) {
            String packageName = typeName.substring(0, typeName.lastIndexOf('.'));
            if (classLoader == InjectionBase.class.getClassLoader()
                    && InjectionBase.class.getPackage().getName().equals(packageName)) {
                return InjectionBase.class;
            } else {
                synchronized (this) {
                    String name;
                    int suffix = injectonBaseSuffix;
                    do {
                        name =
                                packageName
                                        + "."
                                        + InjectionBase.class.getSimpleName()
                                        + "$"
                                        + suffix++;
                        try {
                            Class<?> type = Class.forName(name, false, classLoader);
                            // The injected type must be defined in the class loader that is target
                            // of the injection. Otherwise,
                            // the class's unnamed module would differ from the intended module. To
                            // avoid conflicts, we increment
                            // the suffix until we hit a class with a known name and generate one if
                            // it does not exist.
                            if (type.getClassLoader() == classLoader) {
                                return type;
                            }
                        } catch (ClassNotFoundException ignored) {
                            break;
                        }
                    } while (true);
                    return byteBuddy
                            .subclass(Object.class, ConstructorStrategy.Default.NO_CONSTRUCTORS)
                            .name(name)
                            .make()
                            .load(
                                    classLoader,
                                    loader.resolveStrategy(InjectionBase.class, classLoader, false))
                            .getLoaded();
                }
            }
        }
```

### Buggy: 1 (Commit: a759a950f7b15e32a4b6b9cbc86b10de01726dad)
**Repo**: lucene
```java
public void testConjunction() throws IOException {
    final int iters = atLeast(100);
    for (int iter = 0; iter < iters; ++iter) {
      final int maxDoc = TestUtil.nextInt(random(), 100, 10000);
      final int numIterators = TestUtil.nextInt(random(), 2, 5);
      final FixedBitSet[] sets = new FixedBitSet[numIterators];
      final Scorer[] iterators = new Scorer[numIterators];
      for (int i = 0; i < iterators.length; ++i) {
        final FixedBitSet set = randomSet(maxDoc);
        switch (random().nextInt(3)) {
          case 0:
            // simple iterator
            sets[i] = set;
            iterators[i] =
                new ConstantScoreScorer(
                    0f, ScoreMode.TOP_SCORES, anonymizeIterator(new BitDocIdSet(set).iterator()));
            break;
          case 1:
            // bitSet iterator
            sets[i] = set;
            iterators[i] =
                new ConstantScoreScorer(0f, ScoreMode.TOP_SCORES, new BitDocIdSet(set).iterator());
            break;
          default:
            // scorer with approximation
            final FixedBitSet confirmed = clearRandomBits(set);
            sets[i] = confirmed;
            final TwoPhaseIterator approximation =
                approximation(new BitDocIdSet(set).iterator(), confirmed);
            iterators[i] = scorer(approximation);
            break;
        }
      }

      final DocIdSetIterator conjunction =
          ConjunctionUtils.intersectScorers(Arrays.asList(iterators));
      assertEquals(intersect(sets), toBitSet(maxDoc, conjunction));
    }
  }
```

### Buggy: 1 (Commit: 1b00e6e021b55479d10d833373dd2636712c21fa)
**Repo**: elasticsearch
```java
public void testHasDataReturnsTrueWhenDataSourcesPresent() {
        DataSource ds = new DataSource("s3", "s3", null, Map.of());
        assertTrue(handler.hasData(new DataSourceMetadata(Map.of("s3", ds))));
    }
```

### Buggy: 1 (Commit: b843b4c6c395cff92b72997c8f59b0579d68365d)
**Repo**: lucene
```java
@Override
          public BytesRef binaryValue() throws IOException {
            long startOffset = addresses.get(doc);
            bytes.length = (int) (addresses.get(doc + 1L) - startOffset);
            bytesSlice.readBytes(startOffset, bytes.bytes, 0, bytes.length);
            return bytes;
          }
```

### Buggy: 0 (Commit: d860752657047435096cff155fa4c04267014122)
**Repo**: guava
```java
boolean canDecode(char ch) {
      return ch <= Ascii.MAX && decodabet[ch] != -1;
    }
```

### Buggy: 0 (Commit: ae85262f04df19b6307de18758cfdcc31cae733d)
**Repo**: commons-lang
```java
@Test
    void testSplit_String() {
        assertNull(StringUtils.split(null));
        assertEquals(0, StringUtils.split("").length);

        String str = "a b  .c";
        String[] res = StringUtils.split(str);
        assertEquals(3, res.length);
        assertEquals("a", res[0]);
        assertEquals("b", res[1]);
        assertEquals(".c", res[2]);

        str = " a ";
        res = StringUtils.split(str);
        assertEquals(1, res.length);
        assertEquals("a", res[0]);

        str = "a" + WHITESPACE + "b" + NON_WHITESPACE + "c";
        res = StringUtils.split(str);
        assertEquals(2, res.length);
        assertEquals("a", res[0]);
        assertEquals("b" + NON_WHITESPACE + "c", res[1]);
    }
```

### Buggy: 0 (Commit: b60d9f03e87f2f235c8d7ab41365d8d1ed637149)
**Repo**: junit5
```java
@AfterEach
	void resetSystemProperty() {
		System.clearProperty(KEY);
	}
```

### Buggy: 1 (Commit: c5ca245c09af5c24b80832bdf54beaddc6c670f8)
**Repo**: elasticsearch
```java
public void testMvIntersectsPrunesPartitionOutsideTheSet() {
        Literal set = new Literal(SRC, List.of(2023, 2024), DataType.INTEGER);
        Expression filter = new MvIntersects(SRC, fieldAttr("year"), set);
        assertEquals(Boolean.TRUE, FileSplitProvider.evaluateFilter(filter, Map.of("year", 2024)));
        assertEquals(Boolean.FALSE, FileSplitProvider.evaluateFilter(filter, Map.of("year", 2022)));
    }
```

### Buggy: 1 (Commit: 088e1eb1a58b6d91c6e77a8c9e1932bb387bc0e7)
**Repo**: lucene
```java
public void setScore(int globalOrdinal, float score) {
      int block = globalOrdinal / arraySize;
      int offset = globalOrdinal % arraySize;
      float[] scores = blocks[block];
      if (scores == null) {
        blocks[block] = scores = new float[arraySize];
        if (unset != 0f) {
          Arrays.fill(scores, unset);
        }
      }
      scores[offset] = score;
    }
```

### Buggy: 1 (Commit: 45f08d9e3b03177e12559878fc95cf3266b65052)
**Repo**: commons-lang
```java
@Override
            public String getTypeName() {
                return "Unsupported";
            }
```

### Buggy: 0 (Commit: b02f7ddea361d7f026dc241a6cc6408e275b3e05)
**Repo**: spring-boot
```java
@Test
	protected void servletContextListenerContextDestroyedIsNotCalledWhenContainerIsStopped() throws Exception {
		ServletContextListener listener = mock(ServletContextListener.class);
		this.webServer = getFactory().getWebServer((servletContext) -> servletContext.addListener(listener));
		this.webServer.start();
		this.webServer.stop();
		then(listener).should(never()).contextDestroyed(any(ServletContextEvent.class));
	}
```

### Buggy: 1 (Commit: 7e5906fb0cb679d630527fc1bc18018f935518dc)
**Repo**: commons-lang
```java
static boolean getForceAccessible() {
        return SystemProperties.getBoolean(AbstractReflection.class, "forceAccessible", () -> true);
    }
```

### Buggy: 0 (Commit: 917352266b61870c47a7da97965778f0288d50cb)
**Repo**: mockito
```java
@SuppressWarnings("unchecked")
    public CreationSettings(CreationSettings copy) {
        // TODO can we have a reflection test here? We had a couple of bugs here in the past.
        this.typeToMock = copy.typeToMock;
        this.genericTypeToMock = copy.genericTypeToMock;
        this.extraInterfaces = copy.extraInterfaces;
        this.name = copy.name;
        this.spiedInstance = copy.spiedInstance;
        this.defaultAnswer = copy.defaultAnswer;
        this.mockName = copy.mockName;
        this.serializableMode = copy.serializableMode;
        this.invocationListeners = copy.invocationListeners;
        this.stubbingLookupListeners = copy.stubbingLookupListeners;
        this.verificationStartedListeners = copy.verificationStartedListeners;
        this.stubOnly = copy.stubOnly;
        this.useConstructor = copy.isUsingConstructor();
        this.outerClassInstance = copy.getOuterClassInstance();
        this.constructorArgs = copy.getConstructorArgs();
        this.strictness = copy.strictness;
        this.stripAnnotations = copy.stripAnnotations;
        this.mockMaker = copy.mockMaker;
    }
```

### Buggy: 1 (Commit: 301ec2916d9698be2b079b7c307e06ada72cc1a6)
**Repo**: junit5
```java
@Override
	public <T> Optional<T> getRawConfigurationParameter(String key, Function<? super String, ? extends T> transformer) {
		return configurationParameters.get(key, transformer);
	}
```

### Buggy: 0 (Commit: 99274e3143c688f30b638fca9bc7057f37c51984)
**Repo**: spring-boot
```java
@Override
	public @Nullable String getBase() {
		return this.properties.getBase();
	}
```

### Buggy: 0 (Commit: 72dd370d951967fe97756ecaaa938c7cb5bcbc28)
**Repo**: guava
```java
public void testParseLongThrowsExceptionForInvalidRadix() {
    // Valid radix values are Character.MIN_RADIX to Character.MAX_RADIX, inclusive.
    assertThrows(
        NumberFormatException.class,
        () -> UnsignedLongs.parseUnsignedLong("0", Character.MIN_RADIX - 1));

    assertThrows(
        NumberFormatException.class,
        () -> UnsignedLongs.parseUnsignedLong("0", Character.MAX_RADIX + 1));

    // The radix is used as an array index, so try a negative value.
    assertThrows(NumberFormatException.class, () -> UnsignedLongs.parseUnsignedLong("0", -1));
  }
```

### Buggy: 0 (Commit: d6cb32351d3299df05a27c04dfbd7b663d3d7821)
**Repo**: mockito
```java
@Test
    public void should_init_spy_by_instance() throws Exception {
        doReturn("foo").when(spiedList).get(10);
        assertEquals("foo", spiedList.get(10));
        assertTrue(spiedList.isEmpty());
    }
```

### Buggy: 1 (Commit: d000e630775cfa45752eeb491a197283e7370621)
**Repo**: mockito
```java
protected SubclassBytecodeGenerator(
            SubclassLoader loader,
            Implementation readReplace,
            ElementMatcher<? super MethodDescription> matcher) {
        this.loader = loader;
        this.readReplace = readReplace;
        this.matcher = matcher;
        byteBuddy = new ByteBuddy().with(TypeValidation.DISABLED);
        handler = ModuleHandler.make(byteBuddy, loader);
    }
```

### Buggy: 1 (Commit: 87b09ca5c44b6f7d028c8adafe390acb2a8cc70f)
**Repo**: elasticsearch
```java
public void testDifferenceFailsWhenACountLessThanBCount() {
        ExponentialHistogram a = ExponentialHistogram.create(100, breaker(), 1.0, 2.0);
        autoReleaseOnTestEnd((ReleasableExponentialHistogram) a);
        ExponentialHistogram b = ExponentialHistogram.create(100, breaker(), 1.0, 2.0, 3.0);
        autoReleaseOnTestEnd((ReleasableExponentialHistogram) b);

        try (ExponentialHistogramMerger merger = ExponentialHistogramMerger.create(breaker())) {
            IllegalArgumentException e = expectThrows(IllegalArgumentException.class, () -> merger.setToDifference(a, b));
            assertThat(e.getMessage(), containsString("a.count < b.count"));
        }
    }
```

### Buggy: 0 (Commit: 5a29b8780f1f18b527e102c4126da7abc0abaca1)
**Repo**: junit5
```java
ExtensionContext get(TestInstantiationAwareExtension extension);
```

### Buggy: 0 (Commit: b60d9f03e87f2f235c8d7ab41365d8d1ed637149)
**Repo**: junit5
```java
@Test
	void getValueInExtensionContext() {
		var summary = new SummaryGeneratingListener();
		var request = LauncherDiscoveryRequestBuilder.request() //
				.configurationParameter("thing", "one else!") //
				.selectors(DiscoverySelectors.selectClass(Something.class)) //
				.forExecution() //
				.listeners(summary) //
				.build();
		LauncherFactory.create().execute(request);
		assertEquals(0, summary.getSummary().getTestsFailedCount());
	}
```

### Buggy: 0 (Commit: 7f8b51413a8cc2dfadaba137144815932e7b243f)
**Repo**: commons-lang
```java
@Override
        public boolean hasNext() {
            return hasNext;
        }
```

### Buggy: 0 (Commit: 99274e3143c688f30b638fca9bc7057f37c51984)
**Repo**: spring-boot
```java
@Bean
	@ConditionalOnMissingBean
	LdapContextSource ldapContextSource(LdapConnectionDetails connectionDetails, LdapProperties properties,
			ObjectProvider<DirContextAuthenticationStrategy> dirContextAuthenticationStrategy) {
		LdapContextSource source = new LdapContextSource();
		dirContextAuthenticationStrategy.ifUnique(source::setAuthenticationStrategy);
		PropertyMapper propertyMapper = PropertyMapper.get();
		propertyMapper.from(connectionDetails.getUsername()).to(source::setUserDn);
		propertyMapper.from(connectionDetails.getPassword()).to(source::setPassword);
		propertyMapper.from(properties.getAnonymousReadOnly()).to(source::setAnonymousReadOnly);
		propertyMapper.from(properties.getReferral())
			.as(((referral) -> referral.name().toLowerCase(Locale.ROOT)))
			.to(source::setReferral);
		propertyMapper.from(connectionDetails.getBase()).to(source::setBase);
		propertyMapper.from(connectionDetails.getUrls()).to(source::setUrls);
		source.setBaseEnvironmentProperties(baseEnvironmentProperties(connectionDetails, properties));
		return source;
	}
```

### Buggy: 1 (Commit: d000e630775cfa45752eeb491a197283e7370621)
**Repo**: mockito
```java
@Test
    public void can_define_class_in_open_java_util_module() throws Exception {
        assumeThat(Plugins.getMockMaker() instanceof InlineByteBuddyMockMaker, is(false));

        Path jar = modularJar(true, true, true);
        ModuleLayer layer = layer(jar, true, namedModules);

        ClassLoader loader = layer.findLoader("mockito.test");
        Class<?> type = loader.loadClass("java.util.concurrent.locks.Lock");

        ClassLoader contextLoader = Thread.currentThread().getContextClassLoader();
        Thread.currentThread().setContextClassLoader(loader);
        try {
            Class<?> mockito = loader.loadClass(Mockito.class.getName());
            @SuppressWarnings("unchecked")
            Lock mock = (Lock) mockito.getMethod("mock", Class.class).invoke(null, type);
            Object stubbing = mockito.getMethod("when", Object.class).invoke(null, mock.tryLock());
            loader.loadClass(OngoingStubbing.class.getName())
                    .getMethod("thenReturn", Object.class)
                    .invoke(stubbing, true);

            boolean relocated =
                    !Boolean.getBoolean("org.mockito.internal.noUnsafeInjection")
                            && ClassInjector.UsingReflection.isAvailable();
            String prefix =
                    relocated
                            ? "org.mockito.codegen.Lock$MockitoMock$"
                            : "java.util.concurrent.locks.Lock$MockitoMock$";
            assertThat(mock.getClass().getName()).startsWith(prefix);
            assertThat(mock.tryLock()).isEqualTo(true);
        } finally {
            Thread.currentThread().setContextClassLoader(contextLoader);
        }
    }
```

### Buggy: 1 (Commit: 27a9d812f66bdbcb0400166a4a402d6ae9e1ce4c)
**Repo**: kafka
```java
@Test
    public void shouldStageWhenTheReplicaOnTheTargetProcessIsNotCaughtUpYet() {
        final Map<String, StreamsGroupMember> members = Map.of(
            "memberA", member("memberA", "processA", mkTasksTuple(TaskRole.ACTIVE, mkTasks(STATEFUL, 0))),
            "memberB", member("memberB", "processB", mkTasksTuple(TaskRole.STANDBY, mkTasks(STATEFUL, 0)))
        );
        final Map<String, TasksTuple> targetAssignment = Map.of(
            "memberA", TasksTuple.EMPTY,
            "memberB", mkTasksTuple(TaskRole.ACTIVE, mkTasks(STATEFUL, 0))
        );

        final AssignmentRefinerImpl.TaskDecisions decisions = analyze(
            members,
            targetAssignment,
            Map.of("memberB", offsets(0L, 10_000L))
        );

        assertEquals(List.of(), decisions.grantedTasks());
        assertEquals(
            List.of(new AssignmentRefinerImpl.StagedMigration(
                STATEFUL_0,
                "memberA",
                "memberB",
                Optional.of("processB"),
                Optional.of(new AssignmentRefinerImpl.TaskCopy("memberB", "processB", TaskRole.STANDBY, false))
            )),
            decisions.stagedMigrations()
        );
    }
```

### Buggy: 0 (Commit: d00566ae5dc1ea0869c0bf84e65053bde433c8b8)
**Repo**: spring-boot
```java
public JmsHealthIndicator(ConnectionFactory connectionFactory) {
		super("JMS health check failed");
		this.connectionFactory = connectionFactory;
	}
```

### Buggy: 1 (Commit: 915ed6e4f98896192908ad94ea6e00cd92879d7a)
**Repo**: mockito
```java
@Override
    public MockCreationSettings getMockSettings() {
        return null;
    }
```

### Buggy: 1 (Commit: c26e7f5016beead77566e2044f8ced8b93259380)
**Repo**: elasticsearch
```java
public void testFullTextAfterSubqueryMatchesSubqueryFirstMultiSourceMessage() {
        String query = "FROM (FROM message_types | KEEP type | DROP type),no_mapping_sample_data,service_owners "
            + "| WHERE match_phrase(service_id, \"fox world\")";
        String error = "verification_exception: line 1:91: [MatchPhrase] function cannot be used after "
            + "(from message_types | keep type | drop type),no_mapping_sample_data,service_owners";

        assertTrue(GenerativeRestTest.isFullTextAfterSubqueryInFromBug(error, query));
    }
```

### Buggy: 1 (Commit: 26f92e80d844e94896e275f38943a64848f6567a)
**Repo**: kafka
```java
@Test
    public void shouldRejectMultiBrokerBootstrap() {
        // The proxy rewrites all routing to itself and forwards to a single upstream broker, so a
        // multi-broker bootstrap must fail fast rather than silently proxy only the first broker.
        final IllegalArgumentException e = assertThrows(IllegalArgumentException.class,
                () -> KafkaProtocolFaultProxy.inFrontOf("localhost:9092,localhost:9093,localhost:9094"));
        assertTrue(e.getMessage().contains("single broker"), e.getMessage());
        assertTrue(e.getMessage().contains("3 servers"), e.getMessage());
    }
```

### Buggy: 1 (Commit: 5c9d8ca5fe6b9a9e200a459d479f5ea636c20050)
**Repo**: kafka
```java
public void replaceSegments(List<LogSegment> newSegments, List<LogSegment> oldSegments) throws IOException {
        synchronized (lock) {
            localLog.checkIfMemoryMappedBufferClosed();
            List<LogSegment> deletedSegments = LocalLog.replaceSegments(localLog.segments(), newSegments, oldSegments, dir(), topicPartition(),
                    config(), scheduler(), logDirFailureChannel(), logIdent, false);
            deleteProducerSnapshots(deletedSegments, true);
        }
    }
```

### Buggy: 1 (Commit: 1a6598c51336de5611632fc672848919b0abfec3)
**Repo**: commons-lang
```java
@Test
    void testCycleMutuallyReferential() {
        final MutualDiffableNode a = new MutualDiffableNode("node");
        final MutualDiffableNode b = new MutualDiffableNode("node");
        a.other = b;
        b.other = a;

        final MutualDiffableNode c = new MutualDiffableNode("node");
        final MutualDiffableNode d = new MutualDiffableNode("node");
        c.other = d;
        d.other = c;

        final DiffResult<MutualDiffableNode> result = a.diff(c);
        assertEquals(0, result.getNumberOfDiffs());
        assertTrue(ReflectionDiffBuilder.getRegistry().isEmpty(), "Registry must be empty after diff");
    }
```

### Buggy: 0 (Commit: 45f08d9e3b03177e12559878fc95cf3266b65052)
**Repo**: commons-lang
```java
@Test
    void testWildcardTypeBuilderDefensiveCopy() {
        // Upper bounds defensive copying on input array and getter
        final Type[] upperBounds = { String.class };
        final WildcardType wildcardUpper = TypeUtils.wildcardType().withUpperBounds(upperBounds).build();
        upperBounds[0] = Integer.class;
        assertArrayEquals(new Type[] { String.class }, wildcardUpper.getUpperBounds());
        wildcardUpper.getUpperBounds()[0] = Integer.class;
        assertArrayEquals(new Type[] { String.class }, wildcardUpper.getUpperBounds());

        // Lower bounds defensive copying on input array and getter
        final Type[] lowerBounds = { String.class };
        final WildcardType wildcardLower = TypeUtils.wildcardType().withLowerBounds(lowerBounds).build();
        lowerBounds[0] = Integer.class;
        assertArrayEquals(new Type[] { String.class }, wildcardLower.getLowerBounds());
        wildcardLower.getLowerBounds()[0] = Integer.class;
        assertArrayEquals(new Type[] { String.class }, wildcardLower.getLowerBounds());
    }
```

### Buggy: 1 (Commit: d74371539f821f52d0ed79188afd8a76e0c183fe)
**Repo**: commons-lang
```java
public boolean contains(final char ch) {
        synchronized (set) {
            return set.stream().anyMatch(range -> range.contains(ch));
        }
    }
```

### Buggy: 1 (Commit: 79152348ece2de85559eb2eb18133862d492c892)
**Repo**: guava
```java
@Override
    public int size() {
      return fromList.size();
    }
```

### Buggy: 0 (Commit: e4969ebe61e26e7ae507081f879493b1c30ed857)
**Repo**: junit5
```java
@Override
	public void interceptTestTemplateMethod(Invocation<@Nullable Void> invocation,
			ReflectiveInvocationContext<Method> invocationContext, ExtensionContext extensionContext) throws Throwable {
		InvocationInterceptor.super.interceptTestTemplateMethod(invocation, invocationContext, extensionContext);
	}
```

### Buggy: 0 (Commit: b02f7ddea361d7f026dc241a6cc6408e275b3e05)
**Repo**: spring-boot
```java
@Contract("!null -> !null")
		private @Nullable Set<jakarta.servlet.SessionTrackingMode> unwrap(
				@Nullable Set<Session.SessionTrackingMode> modes) {
			if (modes == null) {
				return null;
			}
			Set<jakarta.servlet.SessionTrackingMode> result = new LinkedHashSet<>();
			for (Session.SessionTrackingMode mode : modes) {
				result.add(jakarta.servlet.SessionTrackingMode.valueOf(mode.name()));
			}
			return result;
		}
```

### Buggy: 0 (Commit: 5c9d8ca5fe6b9a9e200a459d479f5ea636c20050)
**Repo**: kafka
```java
IndexValue(T index) {
            this.index = index;
        }
```

### Buggy: 0 (Commit: 82d73908cb1804fdeacc560e2e6ade8c94db08c7)
**Repo**: lucene
```java
public abstract KnnVectorValues copy() throws IOException;
```

### Buggy: 1 (Commit: 45f08d9e3b03177e12559878fc95cf3266b65052)
**Repo**: commons-lang
```java
@Test
    void testGClassToString() {
        assertEquals("org.apache.commons.lang3.reflect.AClass.GClass<T extends org.apache.commons.lang3.reflect.AClass.BClass<? extends T> "
                + "& org.apache.commons.lang3.reflect.AClass.AInterface<org.apache.commons.lang3.reflect.AClass.AInterface<? super T>>>",
                TypeUtils.toString(AClass.GClass.class));
    }
```

