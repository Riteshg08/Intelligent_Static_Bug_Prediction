# Python Label Samples

Reviewing label noise: True SZZ can erroneously label refactoring or style changes as bugs if keywords match.

### Buggy: 1 (Commit: bf982718cf30615f2dd17fa71fe17d565ebb1d3e)
**Repo**: flask
```python
def add_url_rule(
        self,
        rule: str,
        endpoint: t.Optional[str] = None,
        view_func: t.Optional[t.Callable] = None,
        **options: t.Any,
    ) -> None:
        """Like :meth:`Flask.add_url_rule` but for a blueprint.  The endpoint for
        the :func:`url_for` function is prefixed with the name of the blueprint.
        """
        if endpoint and "." in endpoint:
            raise ValueError("'endpoint' may not contain a dot '.' character.")

        if view_func and hasattr(view_func, "__name__") and "." in view_func.__name__:
            raise ValueError("'view_func' name may not contain a dot '.' character.")

        self.record(lambda s: s.add_url_rule(rule, endpoint, view_func, **options))
```

### Buggy: 0 (Commit: fb32a564ccc6f91d4b7594f5707c62fab0c11c04)
**Repo**: django
```python
def cached_col(self):
        from django.db.models.expressions import Col

        return Col(self.model._meta.db_table, self, self.output_field)
```

### Buggy: 1 (Commit: 7847227a3fecde4b2a169552b84c60c6286b6025)
**Repo**: django
```python
def test_permission_rename(self):
        # Create initial content type and permissions for OldModel.
        call_command("migrate", "auth_tests", "0001", verbosity=0)
        # Apply the migration that renames OldModel to NewModel.
        call_command("migrate", "auth_tests", "0002", verbosity=0)

        actions = ContentType._meta.default_permissions

        for action in actions:
            self.assertFalse(
                Permission.objects.filter(codename=f"{action}_oldmodel").exists()
            )
            self.assertTrue(
                Permission.objects.filter(codename=f"{action}_newmodel").exists()
            )

        # Unapply that migration, renaming NewModel back to OldModel.
        call_command(
            "migrate",
            "auth_tests",
            "0001",
            database="default",
            interactive=False,
            verbosity=0,
        )

        for action in actions:
            self.assertTrue(
                Permission.objects.filter(codename=f"{action}_oldmodel").exists()
            )
            self.assertFalse(
                Permission.objects.filter(codename=f"{action}_newmodel").exists()
            )

        call_command(
            "migrate",
            "auth_tests",
            "zero",
            database="default",
            interactive=False,
            verbosity=0,
        )
```

### Buggy: 0 (Commit: 3db0898eee4061d44de5052953ef0fe3afb5951f)
**Repo**: django
```python
def test_uuid7_shift(self):
        shift = timedelta(minutes=1)
        now = datetime.now(timezone.utc)
        m = UUIDModel.objects.create(uuid=UUID7(shift))
        ts = int.from_bytes(m.uuid.bytes[:6])
        uuid_timestamp = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.assertAlmostEqual(
            (uuid_timestamp - now).total_seconds(), shift.total_seconds(), places=1
        )
```

### Buggy: 0 (Commit: a8cc3f122b9b61b11930a33a62aa7a4481382100)
**Repo**: pytest
```python
def expr(s: Scanner) -> ast.expr:
    ret = and_expr(s)
    while s.accept(TokenType.OR):
        rhs = and_expr(s)
        ret = ast.BoolOp(ast.Or(), [ret, rhs])
    return ret
```

### Buggy: 1 (Commit: 58a47d6b8e231d8800910d4c0ed8941e4c994ecb)
**Repo**: scikit-learn
```python
def test_error_norm_array_api(array_namespace, device_name, dtype_name, norm):
    """error_norm() should work with array API inputs."""
    xp, device = _array_api_for_tests(array_namespace, device_name, dtype_name)

    X_np = X.astype(dtype_name, copy=False)
    X_xp = xp.asarray(X_np, device=device)

    lw_np = LedoitWolf().fit(X_np)
    comp_cov_np = empirical_covariance(X_np)

    with config_context(array_api_dispatch=True):
        lw_xp = LedoitWolf().fit(X_xp)
        # Downcast to target dtype before converting because `empirical_covariance` can
        # return float64 for numpy and MPS only supports float32
        comp_cov_xp = xp.asarray(comp_cov_np.astype(dtype_name), device=device)
        result_xp = lw_xp.error_norm(comp_cov_xp, norm=norm)

    result_np = lw_np.error_norm(comp_cov_np, norm=norm)
    assert_allclose(result_np, float(result_xp), atol=_atol_for_type(dtype_name))
```

### Buggy: 1 (Commit: c47fedf475e6c6724ca442ee59b60fee89e1c988)
**Repo**: pytest
```python
def test_rewrite_picks_up_edit_within_one_mtime_second(
        self, pytester: Pytester
    ) -> None:
        """Regression test for #13292.

        The pyc header can only hold a whole-second timestamp, so a file
        edited twice within the same second used to be served from a stale
        pyc. Hashing the source instead sidesteps the resolution problem.
        """
        source = pytester.path / "test_edited.py"
        pyc_dir = source.parent / "__pycache__"

        # both revisions are the same size, so only the content differs
        before = "def test_aaa(): assert True\n"
        after = "def test_bbb(): assert None\n"
        assert len(before) == len(after)

        source.write_text(before, encoding="utf-8")
        assert pytester.runpytest_subprocess("-q").ret == 0
        (pyc,) = pyc_dir.glob("test_edited.*.pyc")
        mtime = os.stat(source).st_mtime

        source.write_text(after, encoding="utf-8")
        # pin the mtime so the edit is indistinguishable by timestamp
        os.utime(source, (mtime, mtime))
        assert pyc.exists()  # the pyc written by the first run is still there

        result = pytester.runpytest_subprocess("-q")
        result.stdout.fnmatch_lines(["*test_bbb*"])
        assert result.ret != 0
```

### Buggy: 0 (Commit: 826514b8eb18f6c314cf566630253d35c89e42c3)
**Repo**: flask
```python
def fails():
        1 // 0
```

### Buggy: 1 (Commit: 7090a219ecc8dea577f6abe1ac38dec4861e49d7)
**Repo**: pandas
```python
def astype_array(values: ArrayLike, dtype: DtypeObj, copy: bool = False) -> ArrayLike:
    """
    Cast array (ndarray or ExtensionArray) to the new dtype.

    Parameters
    ----------
    values : ndarray or ExtensionArray
    dtype : dtype object
    copy : bool, default False
        copy if indicated

    Returns
    -------
    ndarray or ExtensionArray
    """
    if values.dtype == dtype:
        if copy:
            return values.copy()
        return values

    if not isinstance(values, np.ndarray):
        # i.e. ExtensionArray
        values = values.astype(dtype, copy=copy)

    else:
        values = _astype_nansafe(values, dtype, copy=copy)

    # in pandas we don't store numpy str dtypes, so convert to object
    if isinstance(dtype, np.dtype) and issubclass(values.dtype.type, str):
        values = np.array(values, dtype=object)

    return values
```

### Buggy: 0 (Commit: 9ca26bdd4bc0e535254f46e05403374352e0ab3b)
**Repo**: scikit-learn
```python
def test_estimator_html_repr_table():
    """Check that we add the table of parameters in the HTML representation."""
    est = LogisticRegression(C=10.0, fit_intercept=False)
    assert "parameters-table" in estimator_html_repr(est)
```

### Buggy: 1 (Commit: 60a17fccf4f2fa31b823b0f938005897f2f3ef16)
**Repo**: django
```python
def setUpTestData(cls):
        LessonEntry.objects.bulk_create(
            LessonEntry(id=id_, name1=name1, name2=name2)
            for id_, name1, name2 in [
                (1, "einfach", "simple"),
                (2, "schwierig", "difficult"),
            ]
        )
        WordEntry.objects.bulk_create(
            WordEntry(id=id_, lesson_entry_id=lesson_entry_id, name=name)
            for id_, lesson_entry_id, name in [
                (1, 1, "einfach"),
                (2, 1, "simple"),
                (3, 2, "schwierig"),
                (4, 2, "difficult"),
            ]
        )
```

### Buggy: 1 (Commit: 283acb3c66964be76c66afaf521c5df841ad30e1)
**Repo**: pandas
```python
def __getattr__(self, name):
            return getattr(self.conn, name)
```

### Buggy: 1 (Commit: 3827d66bfbdc568f58cce57b113131598c46cd5a)
**Repo**: ansible
```python
def test_password_with_prompt(self):
        # test with password prompting enabled
        self.pc.password = None
        self.conn.become.prompt = b'Password:'
        self.conn._examine_output.side_effect = self._password_with_prompt_examine_output
        self.mock_popen_res.stdout.read.side_effect = [b"Password:", b"Success", b""]
        self.mock_popen_res.stderr.read.side_effect = [b""]
        self.mock_selector.select.side_effect = [
            [(SelectorKey(self.mock_popen_res.stdout, 1001, [EVENT_READ], None), EVENT_READ)],
            [(SelectorKey(self.mock_popen_res.stdout, 1001, [EVENT_READ], None), EVENT_READ)],
            [(SelectorKey(self.mock_popen_res.stderr, 1002, [EVENT_READ], None), EVENT_READ),
             (SelectorKey(self.mock_popen_res.stdout, 1001, [EVENT_READ], None), EVENT_READ)],
            []]
        self.mock_selector.get_map.side_effect = lambda: True

        return_code, b_stdout, b_stderr = self.conn._run("ssh", "this is input data")
        assert return_code == 0
        assert b_stdout == b''
        assert b_stderr == b''
        assert self.mock_selector.register.called is True
        assert self.mock_selector.register.call_count == 2
        assert self.conn._send_initial_data.called is True
        assert self.conn._send_initial_data.call_count == 1
        assert self.conn._send_initial_data.call_args[0][1] == 'this is input data'
```

### Buggy: 1 (Commit: 141fde1d8ec8663b4be98777750d2f58c6fe44ad)
**Repo**: flask
```python
def _find_error_handler(self, e: Exception) -> t.Optional[ErrorHandlerCallable]:
        """Return a registered error handler for an exception in this order:
        blueprint handler for a specific code, app handler for a specific code,
        blueprint handler for an exception class, app handler for an exception
        class, or ``None`` if a suitable handler is not found.
        """
        exc_class, code = self._get_exc_class_and_code(type(e))

        for c in [code, None]:
            for name in chain(self._request_blueprints(), [None]):
                handler_map = self.error_handler_spec[name][c]

                if not handler_map:
                    continue

                for cls in exc_class.__mro__:
                    handler = handler_map.get(cls)

                    if handler is not None:
                        return handler
        return None
```

### Buggy: 0 (Commit: 5cb825427ce8ae62d0e4f4908dd1980436b2961c)
**Repo**: pandas
```python
def take(
        self,
        indices,
        *,
        allow_fill: bool = False,
        fill_value=None,
        axis=None,
        **kwargs,
    ) -> Self:
        """
        Take elements from the IntervalArray.

        Parameters
        ----------
        indices : sequence of integers
            Indices to be taken.

        allow_fill : bool, default False
            How to handle negative values in `indices`.

            * False: negative values in `indices` indicate positional indices
              from the right (the default). This is similar to
              :func:`numpy.take`.

            * True: negative values in `indices` indicate
              missing values. These values are set to `fill_value`. Any other
              other negative values raise a ``ValueError``.

        fill_value : Interval or NA, optional
            Fill value to use for NA-indices when `allow_fill` is True.
            This may be ``None``, in which case the default NA value for
            the type, ``self.dtype.na_value``, is used.

            For many ExtensionArrays, there will be two representations of
            `fill_value`: a user-facing "boxed" scalar, and a low-level
            physical NA value. `fill_value` should be the user-facing version,
            and the implementation should handle translating that to the
            physical version for processing the take if necessary.

        axis : any, default None
            Present for compat with IntervalIndex; does nothing.

        Returns
        -------
        IntervalArray

        Raises
        ------
        IndexError
            When the indices are out of bounds for the array.
        ValueError
            When `indices` contains negative values other than ``-1``
            and `allow_fill` is True.
        """
        nv.validate_take((), kwargs)

        fill_left = fill_right = fill_value
        if allow_fill:
            fill_left, fill_right = self._validate_scalar(fill_value)

        left_take = take(
            self._left, indices, allow_fill=allow_fill, fill_value=fill_left
        )
        right_take = take(
            self._right, indices, allow_fill=allow_fill, fill_value=fill_right
        )

        return self._shallow_copy(left_take, right_take)
```

### Buggy: 1 (Commit: c9a1f7ad6545c9cc27c41c385f1d4cd9c7cf1a98)
**Repo**: flask
```python
def __init__(self, request):
        exc = request.routing_exception
        buf = [
            f"A request was sent to this URL ({request.url}) but a"
            " redirect was issued automatically by the routing system"
            f" to {exc.new_url!r}."
        ]

        # In case just a slash was appended we can be extra helpful
        if f"{request.base_url}/" == exc.new_url.split("?")[0]:
            buf.append(
                "  The URL was defined with a trailing slash so Flask"
                " will automatically redirect to the URL with the"
                " trailing slash if it was accessed without one."
            )

        buf.append(
            "  Make sure to directly send your"
            f" {request.method}-request to this URL since we can't make"
            " browsers or HTTP clients redirect with form data reliably"
            " or without user interaction."
        )
        buf.append("\n\nNote: this exception is only raised in debug mode")
        AssertionError.__init__(self, "".join(buf).encode("utf-8"))
```

### Buggy: 1 (Commit: fbdae4e7ef2bbb87a7e4b75f6bf445528c0c7157)
**Repo**: pytest
```python
def _diff_text(
    left: str, right: str, highlighter: _HighlightFunc, verbose: int = 0
) -> Iterator[str]:
    """Yield the explanation for the diff between text.

    Unless --verbose is used this will skip leading and trailing
    characters which are identical to keep the diff minimal.
    """
    from difflib import ndiff

    if verbose < 1:
        i = 0  # just in case left or right has zero length
        for i in range(min(len(left), len(right))):
            if left[i] != right[i]:
                break
        if i > 42:
            i -= 10  # Provide some context
            yield f"Skipping {i} identical leading characters in diff, use -v to show"
            left = left[i:]
            right = right[i:]
        if len(left) == len(right):
            for i in range(1, len(left) + 1):
                if left[-i] != right[-i]:
                    break
            if i > 42:
                i -= 10  # Provide some context
                yield (
                    f"Skipping {i} identical trailing "
                    "characters in diff, use -v to show"
                )
                left = left[:-i]
                right = right[:-i]
    keepends = True
    if left.isspace() or right.isspace():
        left = repr(str(left))
        right = repr(str(right))
        yield "Strings contain only whitespace, escaping them using repr()"
    # "right" is the expected base against which we compare "left",
    # see https://github.com/pytest-dev/pytest/issues/3333
    yield from highlighter(
        "\n".join(
            line.strip("\n")
            for line in ndiff(right.splitlines(keepends), left.splitlines(keepends))
        ),
        lexer="diff",
    ).splitlines()
```

### Buggy: 0 (Commit: a712f79bf1cb96390bf7e4eaaa5bac23a9a595fd)
**Repo**: ansible
```python
def _mock_import(name, *args, **kwargs):
            try:
                fromlist = kwargs.get('fromlist', args[2])
            except IndexError:
                fromlist = []
            if name == 'systemd' and 'journal' in fromlist:
                raise ImportError
            return realimport(name, *args, **kwargs)
```

### Buggy: 0 (Commit: 63f2abff4003210103a0569664982ce384487dfa)
**Repo**: scikit-learn
```python
def test_missing_values_random_splitter_on_equal_nodes_no_missing(criterion, seed):
    """Check missing values go to the correct node during predictions for ExtraTree.

    Since ETC use random splits, we use different seeds to verify that the
    left/right node is chosen correctly when the splits occur.
    """
    X = np.array([[0, 1, 2, 3, 8, 9, 11, 12, 15]]).T
    y = np.array([0.1, 0.2, 0.3, 0.2, 1.4, 1.4, 1.5, 1.6, 2.6])

    etr = ExtraTreeRegressor(random_state=seed, max_depth=1, criterion=criterion)
    etr.fit(X, y)

    # Get the left and right children of the root node
    left_child = etr.tree_.children_left[0]
    right_child = etr.tree_.children_right[0]

    # Get the number of samples for the left and right children
    left_samples = etr.tree_.weighted_n_node_samples[left_child]
    right_samples = etr.tree_.weighted_n_node_samples[right_child]
    went_left = left_samples > right_samples

    # predictions
    y_pred_left = etr.tree_.value[left_child][0]
    y_pred_right = etr.tree_.value[right_child][0]

    # Goes to node with the most data points
    y_pred = etr.predict([[np.nan]])
    if went_left:
        assert_allclose(y_pred_left, y_pred)
    else:
        assert_allclose(y_pred_right, y_pred)
```

### Buggy: 1 (Commit: 857849927da6e988d7d026b17aef214d43e5f26e)
**Repo**: scikit-learn
```python
def test_parallel_execution(data, method, ensemble):
    """Test parallel calibration"""
    X, y = data
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    estimator = make_pipeline(StandardScaler(), LinearSVC(random_state=42))

    cal_clf_parallel = CalibratedClassifierCV(
        estimator, method=method, n_jobs=2, ensemble=ensemble
    )
    cal_clf_parallel.fit(X_train, y_train)
    probs_parallel = cal_clf_parallel.predict_proba(X_test)

    cal_clf_sequential = CalibratedClassifierCV(
        estimator, method=method, n_jobs=1, ensemble=ensemble
    )
    cal_clf_sequential.fit(X_train, y_train)
    probs_sequential = cal_clf_sequential.predict_proba(X_test)

    assert_allclose(probs_parallel, probs_sequential)
```

### Buggy: 1 (Commit: 1071baca607be4c273a7e3dfefaf5e2fd7433b5e)
**Repo**: ansible
```python
def _run_module(wrapped_cmd, jid):

    # DTFIX-FUTURE: needs rework for serialization profiles

    jwrite({"started": True, "finished": False, "ansible_job_id": jid})

    result = {}

    # signal grandchild process started and isolated from being terminated
    # by the connection being closed sending a signal to the job group
    ipc_notifier.send(True)
    ipc_notifier.close()

    outdata = ''
    filtered_outdata = ''
    stderr = ''
    try:
        cmd = [to_bytes(c, errors='surrogate_or_strict') for c in shlex.split(wrapped_cmd)]
        # call the module interpreter directly (for non-binary modules)
        # this permits use of a script for an interpreter on non-Linux platforms
        interpreter = _get_interpreter(cmd[0])
        if interpreter:
            cmd = interpreter + cmd
        script = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            text=True,
            encoding="utf-8",
            errors="surrogateescape",
        )

        (outdata, stderr) = script.communicate()

        (filtered_outdata, json_warnings) = _filter_non_json_lines(outdata)

        result = json.loads(filtered_outdata)

        if json_warnings:
            # merge JSON junk warnings with any existing module warnings
            module_warnings = result.get('warnings', [])
            if not isinstance(module_warnings, list):
                module_warnings = [module_warnings]

            # this relies on the controller's fallback conversion of string warnings to WarningMessageDetail instances, and assumes
            # that the module result and warning collection are basic JSON datatypes (eg, no tags or other custom collections).
            module_warnings.extend(json_warnings)
            result['warnings'] = module_warnings

        if stderr:
            result['stderr'] = stderr
        jwrite(result)

    except OSError:
        e = sys.exc_info()[1]
        result = {
            "failed": True,
            "cmd": wrapped_cmd,
            "msg": to_text(e),
            "outdata": outdata,  # temporary notice only
            "stderr": stderr
        }
        result['ansible_job_id'] = jid
        jwrite(result)

    except Exception:
        result = {
            "failed": True,
            "cmd": wrapped_cmd,
            "data": outdata,  # temporary notice only
            "stderr": stderr,
            "msg": traceback.format_exc()
        }
        result['ansible_job_id'] = jid
        jwrite(result)
```

### Buggy: 1 (Commit: 99afbb277d25d3b052e00b9a8da216054d51d62a)
**Repo**: flask
```python
def test_nested_blueprint_url_prefix(app, client):
    parent = flask.Blueprint("parent", __name__, url_prefix="/parent")
    child = flask.Blueprint("child", __name__, url_prefix="/child")
    grandchild = flask.Blueprint("grandchild", __name__, url_prefix="/grandchild")
    apple = flask.Blueprint("apple", __name__, url_prefix="/apple")

    @parent.route("/")
    def parent_index():
        return "Parent"

    @child.route("/")
    def child_index():
        return "Child"

    @grandchild.route("/")
    def grandchild_index():
        return "Grandchild"

    @apple.route("/")
    def apple_index():
        return "Apple"

    child.register_blueprint(grandchild)
    child.register_blueprint(apple, url_prefix="/orange")  # test overwrite
    parent.register_blueprint(child)
    app.register_blueprint(parent)

    assert client.get("/parent/").data == b"Parent"
    assert client.get("/parent/child/").data == b"Child"
    assert client.get("/parent/child/grandchild/").data == b"Grandchild"
    assert client.get("/parent/child/orange/").data == b"Apple"
```

### Buggy: 1 (Commit: 7576781cc6718fae313faadd29288ad8c4313f3c)
**Repo**: django
```python
def test_simple_raw_query(self):
        """
        Basic test of raw query with a simple database query
        """
        query = "SELECT * FROM raw_query_author"
        authors = Author.objects.all()
        self.assertSuccessfulRawQuery(Author, query, authors)
```

### Buggy: 0 (Commit: 6c59ff18549a37c1687dcce631d7dffebf7c6861)
**Repo**: ansible
```python
def _deprecate_top_level_fact(value: t.Any) -> t.Any:
    """
    Deprecate the given top-level fact value.
    The inner values are shared to aid in message de-duplication across hosts/values, and reduce intra-process memory usage.
    Unique tag instances are required to achieve the correct de-duplication within a top-level templating operation.
    """
    return _DEPRECATE_TOP_LEVEL_FACT_TAG.tag(value)
```

### Buggy: 1 (Commit: f14e293cd7444e064b9c9ba471fd5aa7e6132ea6)
**Repo**: django
```python
def test_in_bulk_values_list_all(self):
        Article.objects.exclude(pk__in=[self.a1.pk, self.a2.pk]).delete()
        arts = Article.objects.values_list().in_bulk()
        self.assertEqual(
            arts,
            {
                self.a1.pk: (
                    self.a1.pk,
                    "Article 1",
                    self.a1.pub_date,
                    self.au1.pk,
                    "a1",
                ),
                self.a2.pk: (
                    self.a2.pk,
                    "Article 2",
                    self.a2.pub_date,
                    self.au1.pk,
                    "a2",
                ),
            },
        )
```

### Buggy: 1 (Commit: 3af2f456d8c0a90bd6609f2205cd0b2d0f7f800e)
**Repo**: requests
```python
def __enter__(self):
        self.start()
        self.ready_event.wait(self.WAIT_EVENT_TIMEOUT)
        return self.host, self.port
```

### Buggy: 1 (Commit: a51536f311d937ee92f7185fac445ca39b2efefa)
**Repo**: ansible
```python
def save_collection_source(self, collection, url, sha256_hash, token, signatures_url, signatures):
        # type: (Candidate, str, str, GalaxyToken, str, list[dict[str, str]]) -> None
        """Store collection URL, SHA256 hash and Galaxy API token.

        This is a hook that is supposed to be called before attempting to
        download Galaxy-based collections with ``get_galaxy_artifact_path()``.
        """
        self._galaxy_collection_cache[collection] = url, sha256_hash, token
        self._galaxy_collection_origin_cache[collection] = signatures_url, signatures
```

### Buggy: 0 (Commit: cef01730fb97b2a5897cffc02504c7dcaffcb0a2)
**Repo**: ansible
```python
def from_blob(cls, blob: memoryview | bytes) -> t.Self:
        if blob and blob[0] > 127:
            raise ValueError("Invalid data")
        return cls.from_bytes(blob, byteorder='big')
```

### Buggy: 0 (Commit: cef01730fb97b2a5897cffc02504c7dcaffcb0a2)
**Repo**: ansible
```python
def key_data_into_crypto_objects(key_data: bytes, passphrase: bytes | None) -> tuple[CryptoPrivateKey, CryptoPublicKey, str]:
    private_key = serialization.ssh.load_ssh_private_key(key_data, passphrase)
    public_key = private_key.public_key()
    fingerprint = PublicKeyMsg.from_public_key(public_key).fingerprint

    return private_key, public_key, fingerprint
```

### Buggy: 1 (Commit: 1f56dbaeac942a99bf9d83da6745930a33f1cf49)
**Repo**: pandas
```python
def test_kde_df_rot(self):
        pytest.importorskip("scipy")
        df = pd.DataFrame(np.random.default_rng(2).standard_normal((10, 4)))
        ax = df.plot(kind="kde", rot=20, fontsize=5)
        _check_ticks_props(ax, xrot=20, xlabelsize=5, ylabelsize=5)
```

### Buggy: 1 (Commit: 3adecacccf408960128d7cc122e8212a88ae4e9b)
**Repo**: ansible
```python
def _split_multiext(name, min=3, max=4, count=2):
    """Split a multi-part extension from a file name.

    Returns '([name minus extension], extension)'.

    Define the valid extension length (including the '.') with 'min' and 'max',
    'count' sets the number of extensions, counting from the end, to evaluate.
    Evaluation stops on the first file extension that is outside the min and max range.

    If no valid extensions are found, the original ``name`` is returned
    and ``extension`` is empty.

    :arg name: File name or path.
    :kwarg min: Minimum length of a valid file extension.
    :kwarg max: Maximum length of a valid file extension.
    :kwarg count: Number of suffixes from the end to evaluate.

    """
    extension = ''
    for i, sfx in enumerate(reversed(_suffixes(name))):
        if i >= count:
            break

        if min <= len(sfx) <= max:
            extension = '%s%s' % (sfx, extension)
            name = name.rstrip(sfx)
        else:
            # Stop on the first invalid extension
            break

    return name, extension
```

### Buggy: 1 (Commit: a84fd3ed2fc2f4594d6f5206dcbd88068f973517)
**Repo**: celery
```python
def __init__(self, maxsize, iterable=None, bufmaxsize=1000):
        # type: (int, Iterable, int) -> None
        super().__init__()
        self.maxsize = maxsize
        self.bufmaxsize = 1000
        if iterable:
            self.update(iterable)
        self.total = sum(len(buf) for buf in self.items())
```

### Buggy: 0 (Commit: b475463834458781505d7d9e3344da40251f48dd)
**Repo**: ansible
```python
def __str__(self) -> str:
        """Renders the origin in the form of path:line_num:col_num, omitting missing/invalid elements from the right."""
        if self.path:
            value = self.path
        else:
            value = self.description

        if self.line_num and self.line_num > 0:
            value += f':{self.line_num}'

            if self.col_num and self.col_num > 0:
                value += f':{self.col_num}'

        if self.path and self.description:
            value += f' ({self.description})'

        return value
```

### Buggy: 1 (Commit: b12b48035e8edf9ee646409c0adb246b4386888c)
**Repo**: celery
```python
def _slurp(filename):
    # TODO: Handle case when file does not exist
    with codecs.open(filename, 'r', 'utf-8') as read_fh:
        return [line for line in read_fh]
```

### Buggy: 1 (Commit: 908c98c92b2d1820cea4a14dfd0d31ea0917fe69)
**Repo**: ansible
```python
def main():
    module = AnsibleModule(
        argument_spec=dict(
            database=dict(type='str', required=True),
            key=dict(type='str', no_log=False),
            service=dict(type='str'),
            split=dict(type='str'),
            fail_key=dict(type='bool', default=True),
        ),
        supports_check_mode=True,
    )

    colon = ['passwd', 'shadow', 'group', 'gshadow']

    database = module.params['database']
    key = module.params.get('key')
    split = module.params.get('split')
    service = module.params.get('service')
    fail_key = module.params.get('fail_key')

    getent_bin = module.get_bin_path('getent', True)

    if key is not None:
        cmd = [getent_bin, database, key]
    else:
        cmd = [getent_bin, database]

    if service is not None:
        cmd.extend(['-s', service])

    if not split and split is not None:
        module.fail_json(msg="Invalid split value. The value must be a non-empty string")

    if split is None and database in colon:
        split = ':'

    try:
        rc, out, err = module.run_command(cmd)
    except Exception as e:
        module.fail_json(msg=to_native(e))

    msg = "Unexpected failure!"
    dbtree = 'getent_%s' % database
    results = {dbtree: {}}

    if rc == 0:
        seen = {}
        for line in out.splitlines():
            record = line.split(split)

            if record[0] in seen:
                # more than one result for same key, ensure we store in a list
                if seen[record[0]] == 1:
                    results[dbtree][record[0]] = [results[dbtree][record[0]]]

                results[dbtree][record[0]].append(record[1:])
                seen[record[0]] += 1
            else:
                # new key/value, just assign
                results[dbtree][record[0]] = record[1:]
                seen[record[0]] = 1

        module.exit_json(ansible_facts=results)

    elif rc == 1:
        msg = "Missing arguments, or database unknown."
    elif rc == 2:
        msg = "One or more supplied key could not be found in the database."
        if not fail_key:
            results[dbtree][key] = None
            module.exit_json(ansible_facts=results, msg=msg)
    elif rc == 3:
        msg = "Enumeration not supported on this database."

    module.fail_json(msg=msg)
```

### Buggy: 0 (Commit: 341c72db3071523bf1c73cf0d28683a25a728fd6)
**Repo**: pandas
```python
def test_utcnow_deprecated(self):
        # GH#56680
        msg = "Timestamp.utcnow is deprecated"
        with tm.assert_produces_warning(Pandas4Warning, match=msg):
            pd.Timestamp.utcnow()  # noqa: TID251
```

### Buggy: 1 (Commit: 82cc705860c801129a3025b2c5959fda5fd50f37)
**Repo**: scikit-learn
```python
def test_tfidf_transformer_type(X_dtype):
    X = sparse.rand(10, 20000, dtype=X_dtype, random_state=42)
    X_trans = TfidfTransformer().fit_transform(X)
    assert X_trans.dtype == X.dtype
```

### Buggy: 1 (Commit: cc933385e75172cabacb49cfb9fe3571845cb216)
**Repo**: django
```python
def get_main_version(version=None):
    """Return main version (X.Y[.Z]) from VERSION."""
    version = get_complete_version(version)
    parts = 2 if version[2] == 0 else 3
    return ".".join(str(x) for x in version[:parts])
```

### Buggy: 0 (Commit: 82cc705860c801129a3025b2c5959fda5fd50f37)
**Repo**: scikit-learn
```python
def test_quantile_transform_subsampling_disabled():
    """Check the behaviour of `QuantileTransformer` when `subsample=None`."""
    X = np.random.RandomState(0).normal(size=(200, 1))

    n_quantiles = 5
    transformer = QuantileTransformer(n_quantiles=n_quantiles, subsample=None).fit(X)

    expected_references = np.linspace(0, 1, n_quantiles)
    assert_allclose(transformer.references_, expected_references)
    expected_quantiles = np.quantile(X.ravel(), expected_references)
    assert_allclose(transformer.quantiles_.ravel(), expected_quantiles)
```

### Buggy: 1 (Commit: 09d0020ff205d1166b9b541efccf19333ca69c3a)
**Repo**: pytest
```python
def test_show_fixtures_different_files(self, pytester: Pytester) -> None:
        """`--fixtures` only shows fixtures from first file (#833)."""
        pytester.makepyfile(
            test_a='''
            import pytest

            @pytest.fixture
            def fix_a():
                """Fixture A"""
                pass

            def test_a(fix_a):
                pass
        '''
        )
        pytester.makepyfile(
            test_b='''
            import pytest

            @pytest.fixture
            def fix_b():
                """Fixture B"""
                pass

            def test_b(fix_b):
                pass
        '''
        )
        result = pytester.runpytest("--fixtures")
        result.stdout.fnmatch_lines(
            """
            * fixtures defined from test_a *
            fix_a -- test_a.py:4
                Fixture A

            * fixtures defined from test_b *
            fix_b -- test_b.py:4
                Fixture B
        """
        )
```

### Buggy: 1 (Commit: 6a4bf9eec13e035cf10ecc16e462049b4c967e41)
**Repo**: flask
```python
def _fail(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
            raise RuntimeError(
                "Signalling support is unavailable because the blinker"
                " library is not installed."
            )
```

### Buggy: 0 (Commit: a712f79bf1cb96390bf7e4eaaa5bac23a9a595fd)
**Repo**: ansible
```python
def test_plugins__get_paths(self):
        pl = PluginLoader('test', '', 'test', 'test_plugin')
        pl._paths = [PluginPathContext('/path/one', False),
                     PluginPathContext('/path/two', True)]
        self.assertEqual(pl._get_paths(), ['/path/one', '/path/two'])

        # NOT YET WORKING
        # def fake_glob(path):
        #     if path == 'test/*':
        #         return ['test/foo', 'test/bar', 'test/bam']
        #     elif path == 'test/*/*'
        # m._paths = None
        # mock_glob = MagicMock()
        # mock_glob.return_value = []
        # with patch('glob.glob', mock_glob):
        #     pass
```

### Buggy: 1 (Commit: 2c26a4628ad01d1917cf8a7e315cc54b8c61a63c)
**Repo**: pytest
```python
def test_equal_hashable_values(self) -> None:
        # Build equal-but-not-identical values to exercise the ``==`` path
        # rather than the identity shortcut.
        v1, v2 = tuple([1, 2]), tuple([1, 2])
        assert v1 is not v2
        k1, k2 = ParamValueKey(v1, 0), ParamValueKey(v2, 1)
        assert k1 == k2
        assert hash(k1) == hash(k2)
```

### Buggy: 1 (Commit: 73f4629e48031776cefcf3068f652463b1cab816)
**Repo**: celery
```python
def effect(*args, **kwargs):
            if opens.call_count > 1:
                return s.sh
            raise OSError()
```

### Buggy: 1 (Commit: 26bea1e498d6e234fbc9ce8e07c0389bac73810b)
**Repo**: requests
```python
def send(
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):
        """Sends PreparedRequest object. Returns Response object.

        :param request: The :class:`PreparedRequest <PreparedRequest>` being sent.
        :param stream: (optional) Whether to stream the request content.
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple or urllib3 Timeout object
        :param verify: (optional) Either a boolean, in which case it controls whether
            we verify the server's TLS certificate, or a string, in which case it
            must be a path to a CA bundle to use
        :param cert: (optional) Any user-provided SSL certificate to be trusted.
        :param proxies: (optional) The proxies dictionary to apply to the request.
        :rtype: requests.Response
        """

        try:
            conn = self.get_connection(request.url, proxies)
        except LocationValueError as e:
            raise InvalidURL(e, request=request)

        self.cert_verify(conn, request.url, verify, cert)
        url = self.request_url(request, proxies)
        self.add_headers(
            request,
            stream=stream,
            timeout=timeout,
            verify=verify,
            cert=cert,
            proxies=proxies,
        )

        chunked = not (request.body is None or "Content-Length" in request.headers)

        if isinstance(timeout, tuple):
            try:
                connect, read = timeout
                timeout = TimeoutSauce(connect=connect, read=read)
            except ValueError:
                raise ValueError(
                    f"Invalid timeout {timeout}. Pass a (connect, read) timeout tuple, "
                    f"or a single float to set both timeouts to the same value."
                )
        elif isinstance(timeout, TimeoutSauce):
            pass
        else:
            timeout = TimeoutSauce(connect=timeout, read=timeout)

        try:
            if not chunked:
                resp = conn.urlopen(
                    method=request.method,
                    url=url,
                    body=request.body,
                    headers=request.headers,
                    redirect=False,
                    assert_same_host=False,
                    preload_content=False,
                    decode_content=False,
                    retries=self.max_retries,
                    timeout=timeout,
                )

            # Send the request.
            else:
                if hasattr(conn, "proxy_pool"):
                    conn = conn.proxy_pool

                low_conn = conn._get_conn(timeout=DEFAULT_POOL_TIMEOUT)

                try:
                    skip_host = "Host" in request.headers
                    low_conn.putrequest(
                        request.method,
                        url,
                        skip_accept_encoding=True,
                        skip_host=skip_host,
                    )

                    for header, value in request.headers.items():
                        low_conn.putheader(header, value)

                    low_conn.endheaders()

                    for i in request.body:
                        low_conn.send(hex(len(i))[2:].encode("utf-8"))
                        low_conn.send(b"\r\n")
                        low_conn.send(i)
                        low_conn.send(b"\r\n")
                    low_conn.send(b"0\r\n\r\n")

                    # Receive the response from the server
                    r = low_conn.getresponse()

                    resp = HTTPResponse.from_httplib(
                        r,
                        pool=conn,
                        connection=low_conn,
                        preload_content=False,
                        decode_content=False,
                    )
                except Exception:
                    # If we hit any problems here, clean up the connection.
                    # Then, raise so that we can handle the actual exception.
                    low_conn.close()
                    raise

        except (ProtocolError, OSError) as err:
            raise ConnectionError(err, request=request)

        except MaxRetryError as e:
            if isinstance(e.reason, ConnectTimeoutError):
                # TODO: Remove this in 3.0.0: see #2811
                if not isinstance(e.reason, NewConnectionError):
                    raise ConnectTimeout(e, request=request)

            if isinstance(e.reason, ResponseError):
                raise RetryError(e, request=request)

            if isinstance(e.reason, _ProxyError):
                raise ProxyError(e, request=request)

            if isinstance(e.reason, _SSLError):
                # This branch is for urllib3 v1.22 and later.
                raise SSLError(e, request=request)

            raise ConnectionError(e, request=request)

        except ClosedPoolError as e:
            raise ConnectionError(e, request=request)

        except _ProxyError as e:
            raise ProxyError(e)

        except (_SSLError, _HTTPError) as e:
            if isinstance(e, _SSLError):
                # This branch is for urllib3 versions earlier than v1.22
                raise SSLError(e, request=request)
            elif isinstance(e, ReadTimeoutError):
                raise ReadTimeout(e, request=request)
            elif isinstance(e, _InvalidHeader):
                raise InvalidHeader(e, request=request)
            else:
                raise

        return self.build_response(request, resp)
```

### Buggy: 0 (Commit: 5b10504b5e678f31f52c6edd075e417a901eb3cc)
**Repo**: ansible
```python
def __init__(self, containers: ContainerDatabase, process: t.Optional[SshProcess]) -> None:
        self.containers = containers
        self.process = process
```

### Buggy: 0 (Commit: a3e597c17112da2d9520e27e09159c29ac4b8351)
**Repo**: requests
```python
def rebuild_auth(self, prepared_request, response):
        """When being redirected we may want to strip authentication from the
        request to avoid leaking credentials. This method intelligently removes
        and reapplies authentication where possible to avoid credential loss.
        """
        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            # If we get redirected to a new host, we should strip out any
            # authentication headers.
            original_parsed = urlparse(response.request.url)
            redirect_parsed = urlparse(url)

            if (original_parsed.hostname != redirect_parsed.hostname):
                del headers['Authorization']

        # .netrc might have more auth for us on our new host.
        new_auth = get_netrc_auth(url) if self.trust_env else None
        if new_auth is not None:
            prepared_request.prepare_auth(new_auth)

        return
```

### Buggy: 1 (Commit: 4ffbf5b0d50277295b38abad5ccb00b2608b6f11)
**Repo**: celery
```python
def test_regression_worker_startup_info(self):
        pytest.importorskip('memcache')
        self.app.conf.result_backend = (
            'cache+memcached://127.0.0.1:11211;127.0.0.2:11211;127.0.0.3/'
        )
        worker = self.app.Worker()
        with conftest.stdouts():
            worker.on_start()
            assert worker.startup_info()
```

### Buggy: 1 (Commit: dabb415652dd804c7e58a8bc958f5f02c2d75cab)
**Repo**: pandas
```python
def test_adjoin_unicode(self):
        data = [["あ", "b", "c"], ["dd", "ええ", "ff"], ["ggg", "hhh", "いいい"]]
        expected = "あ  dd  ggg\nb  ええ  hhh\nc  ff  いいい"
        adjoined = printing.adjoin(2, *data)
        assert adjoined == expected

        adj = printing._EastAsianTextAdjustment()

        expected = """あ  dd    ggg
b   ええ  hhh
c   ff    いいい"""

        adjoined = adj.adjoin(2, *data)
        assert adjoined == expected
        cols = adjoined.split("\n")
        assert adj.len(cols[0]) == 13
        assert adj.len(cols[1]) == 13
        assert adj.len(cols[2]) == 16

        expected = """あ       dd         ggg
b        ええ       hhh
c        ff         いいい"""

        adjoined = adj.adjoin(7, *data)
        assert adjoined == expected
        cols = adjoined.split("\n")
        assert adj.len(cols[0]) == 23
        assert adj.len(cols[1]) == 23
        assert adj.len(cols[2]) == 26
```

### Buggy: 1 (Commit: 58a47d6b8e231d8800910d4c0ed8941e4c994ecb)
**Repo**: scikit-learn
```python
def test_ridge_classifier_multilabel_array_api(
    estimator, array_namespace, device_name, dtype_name
):
    xp, device = _array_api_for_tests(array_namespace, device_name, dtype_name)
    X, y = make_multilabel_classification(random_state=0)
    X_np = X.astype(dtype_name)
    y_np = y.astype(dtype_name)
    ridge_np = estimator.fit(X_np, y_np)
    pred_np = ridge_np.predict(X_np)
    classes_np = ridge_np.classes_.copy()
    with config_context(array_api_dispatch=True):
        X_xp, y_xp = xp.asarray(X_np, device=device), xp.asarray(y_np, device=device)
        ridge_xp = estimator.fit(X_xp, y_xp)
        pred_xp = ridge_xp.predict(X_xp)
        assert pred_xp.shape == pred_np.shape == y.shape
        assert_allclose(move_to(pred_xp, xp=np, device="cpu"), pred_np)
        assert_array_equal(move_to(ridge_xp.classes_, xp=np, device="cpu"), classes_np)
```

