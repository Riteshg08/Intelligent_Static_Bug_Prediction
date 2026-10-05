# Go Label Samples

Reviewing label noise: True SZZ can erroneously label refactoring or style changes as bugs if keywords match.

### Buggy: 1 (Commit: bbe9c1e76181df83fdfd6baa6690b5ad050c877a)
**Repo**: moby
```go
func(recvErr chan error) {
		defer close(recvErr)
		for {
			select {
			case <-c.shutdown:
				return
			case <-done:
				return
			default: // proceed
			}

			mh, p, err := ch.recv()
			if err != nil {
				status, ok := status.FromError(err)
				if !ok {
					recvErr <- err
					return
				}

				// in this case, we send an error for that particular message
				// when the status is defined.
				if !sendStatus(mh.StreamID, status) {
					return
				}

				continue
			}

			if mh.StreamID%2 != 1 {
				// enforce odd client initiated identifiers.
				if !sendStatus(mh.StreamID, status.Newf(codes.InvalidArgument, "StreamID must be odd for client initiated streams")) {
					return
				}
				continue
			}

			if mh.Type == messageTypeData {
				i, ok := streams.Load(mh.StreamID)
				if !ok {
					if !sendStatus(mh.StreamID, status.Newf(codes.InvalidArgument, "StreamID is no longer active")) {
						return
					}
					continue
				}
				sh := i.(*streamHandler)
				if mh.Flags&flagNoData != flagNoData {
					unmarshal := func(obj interface{}) error {
						err := protoUnmarshal(p, obj)
						ch.putmbuf(p)
						return err
					}

					if err := sh.data(unmarshal); err != nil {
						if !sendStatus(mh.StreamID, status.Newf(codes.InvalidArgument, "data handling error: %v", err)) {
							return
						}
						continue
					}
				}

				if mh.Flags&flagRemoteClosed == flagRemoteClosed {
					sh.closeSend()
					if len(p) > 0 {
						if !sendStatus(mh.StreamID, status.Newf(codes.InvalidArgument, "data close message cannot include data")) {
							return
						}
						continue
					}
				}
			} else if mh.Type == messageTypeRequest {
				if mh.StreamID <= lastStreamID {
					// enforce odd client initiated identifiers.
					if !sendStatus(mh.StreamID, status.Newf(codes.InvalidArgument, "StreamID cannot be re-used and must increment")) {
						return
					}
					continue

				}
				lastStreamID = mh.StreamID

				// TODO: Make request type configurable
				// Unmarshaller which takes in a byte array and returns an interface?
				var req Request
				if err := c.server.codec.Unmarshal(p, &req); err != nil {
					ch.putmbuf(p)
					if !sendStatus(mh.StreamID, status.Newf(codes.InvalidArgument, "unmarshal request error: %v", err)) {
						return
					}
					continue
				}
				ch.putmbuf(p)

				id := mh.StreamID
				respond := func(status *status.Status, data []byte, streaming, closeStream bool) error {
					select {
					case responses <- response{
						id:          id,
						status:      status,
						data:        data,
						closeStream: closeStream,
						streaming:   streaming,
					}:
					case <-done:
						return ErrClosed
					}
					return nil
				}
				sh, err := c.server.services.handle(ctx, &req, respond)
				if err != nil {
					status, _ := status.FromError(err)
					if !sendStatus(mh.StreamID, status) {
						return
					}
					continue
				}

				streams.Store(id, sh)
				atomic.AddInt32(&active, 1)
			}
			// TODO: else we must ignore this for future compat. log this?
		}
	}
```

### Buggy: 1 (Commit: cdb3c1fc8930899c920578bb987788a5c9131157)
**Repo**: terraform
```go
func TestPlan_Policy_Destroy(t *testing.T) {
	td := t.TempDir()
	testCopyDir(t, testFixturePath("plan-policy"), td)
	t.Chdir(td)

	policyCode := `		resource_policy "resource_type" "policy_name" {
		  enforce_attrs {
		    key = attr.value == "foo"
		  }
		}
	`
	if err := os.WriteFile("policy.hcl", []byte(policyCode), 0644); err != nil {
		t.Fatal(err)
	}

	policyObj := &policy.Policy{
		Result:           policy.AllowResult,
		PolicySetName:    "some_policy_set",
		Address:          "provider_policy.example",
		Directory:        "some/path/to",
		Filename:         "provider_policy_file.tfpolicy.hcl",
		EnforcementLevel: "mandatory",
		Range: &hcl.Range{
			Filename: "provider_policy_file.tfpolicy.hcl",
			Start:    hcl.Pos{Line: 1, Column: 1},
			End:      hcl.Pos{Line: 5, Column: 12},
		},
	}

	originalState := states.BuildState(func(s *states.SyncState) {
		s.SetResourceInstanceCurrent(
			addrs.Resource{
				Mode: addrs.ManagedResourceMode,
				Type: "test_instance",
				Name: "foo",
			}.Instance(addrs.NoKey).Absolute(addrs.RootModuleInstance),
			&states.ResourceInstanceObjectSrc{
				AttrsJSON: []byte(`{"id":"bar"}`),
				Status:    states.ObjectReady,
			},
			addrs.AbsProviderConfig{
				Provider: addrs.NewDefaultProvider("test"),
				Module:   addrs.RootModule,
			},
		)
	})
	statePath := testStateFile(t, originalState)

	p := planFixtureProvider()
	view, done := testView(t)
	overrides := metaOverridesForProvider(p)
	policyClient := policy.NewTestMockClient(t)
	overrides.PolicyClient = policyClient

	providerEvalCount := 0
	policyClient.EvaluateProviderFn = func(ctx context.Context, req policy.EvaluationRequest[*proto.PolicyEvaluateProviderRequest_ProviderMetadata]) policy.EvaluationResponse {
		providerEvalCount++
		return policy.EvaluationResponse{
			Overall:  policy.AllowResult,
			Policies: []*policy.Policy{policyObj},
			Enforcements: []policy.EnforcementResult{{
				Result:  policy.AllowResult,
				Message: "Destroy provider enforcement message",
				Policy:  policyObj,
			}},
		}
	}

	c := &PlanCommand{
		Meta: Meta{
			testingOverrides: overrides,
			View:             view,
		},
	}

	args := []string{"-destroy", "-state", statePath, "-policies", td, "-parallelism=1", "-no-color"}
	code := c.Run(args)
	output := done(t)
	if code != 0 {
		t.Fatalf("bad: %d\n\n%s", code, output.Stderr())
	}

	if providerEvalCount != 1 {
		t.Fatalf("expected exactly 1 provider policy evaluation, got %d", providerEvalCount)
	}

	expectedStdout := `
Warning: Deprecated flag: -state

Use the "path" attribute within the "local" backend to specify a file for
state storage
data.test_data_source.a: Reading...
data.test_data_source.a: Read complete after 0s [id=zzzzz]
test_instance.foo: Refreshing state... [id=bar]

Policy Info:
in policy provider_policy.example
"Destroy provider enforcement message"



Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  - destroy

Terraform will perform the following actions:

  # test_instance.foo will be destroyed
  - resource "test_instance" "foo" {
      - id = "bar" -> null
    }

Plan: 0 to add, 0 to change, 1 to destroy.

─────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't
guarantee to take exactly these actions if you run "terraform apply" now.
`
	if diff := cmp.Diff(expectedStdout, output.Stdout()); diff != "" {
		t.Fatalf("unexpected stdout output:\n%s", diff)
	}

}
```

### Buggy: 1 (Commit: 99d006e6c20e156e0e925fd87bd94816e2f8e9cb)
**Repo**: prometheus
```go
func(t *testing.T) {
			opts := DefaultOptions()
			opts.OutOfOrderTimeWindow = 100
			db := newTestDB(t, withOpts(opts), withRngs(100))

			blocks := []*BlockMeta{
				{MinTime: 100, MaxTime: 200}, // Oldest block
				{MinTime: 200, MaxTime: 300},
				{MinTime: 300, MaxTime: 400},
				{MinTime: 400, MaxTime: 500},
				{MinTime: 500, MaxTime: 600}, // Newest Block
			}

			for _, m := range blocks {
				createBlock(t, db.Dir(), genSeries(100, 10, m.MinTime, m.MaxTime))
			}

			headBlocks := []*BlockMeta{
				{MinTime: 700, MaxTime: 800},
			}

			// Add some data to the WAL.
			headApp := db.Head().AppenderV2(context.Background())
			var aSeries labels.Labels
			var it chunkenc.Iterator
			for _, m := range headBlocks {
				series := genSeries(100, 10, m.MinTime, m.MaxTime+1)
				for _, s := range series {
					aSeries = s.Labels()
					it = s.Iterator(it)
					for it.Next() == chunkenc.ValFloat {
						tim, v := it.At()
						_, err := headApp.Append(0, s.Labels(), 0, tim, v, nil, nil, storage.AOptions{})
						require.NoError(t, err)
					}
					require.NoError(t, it.Err())
				}
			}
			require.NoError(t, headApp.Commit())
			db.Head().mmapHeadChunks()

			require.Eventually(t, func() bool {
				return db.Head().chunkDiskMapper.IsQueueEmpty()
			}, 2*time.Second, 100*time.Millisecond)

			// Test that registered size matches the actual disk size.
			require.NoError(t, db.reloadBlocks())                               // Reload the db to register the new db size.
			require.Len(t, db.Blocks(), len(blocks))                            // Ensure all blocks are registered.
			blockSize := int64(prom_testutil.ToFloat64(db.metrics.blocksBytes)) // Use the actual internal metrics.
			walSize, err := db.Head().wal.Size()
			require.NoError(t, err)
			cdmSize, err := db.Head().chunkDiskMapper.Size()
			require.NoError(t, err)
			require.NotZero(t, cdmSize)
			// Expected size should take into account block size + WAL size + Head
			// chunks size
			expSize := blockSize + walSize + cdmSize
			actSize, err := fileutil.DirSize(db.Dir())
			require.NoError(t, err)
			require.Equal(t, expSize, actSize, "registered size doesn't match actual disk size")

			// Create a WAL checkpoint, and compare sizes.
			first, last, err := wlog.Segments(db.Head().wal.Dir())
			require.NoError(t, err)
			_, err = wlog.Checkpoint(promslog.NewNopLogger(), db.Head().wal, first, last-1, func(chunks.HeadSeriesRef) bool { return false }, 0, enableSTStorage)
			require.NoError(t, err)
			blockSize = int64(prom_testutil.ToFloat64(db.metrics.blocksBytes)) // Use the actual internal metrics.
			walSize, err = db.Head().wal.Size()
			require.NoError(t, err)
			cdmSize, err = db.Head().chunkDiskMapper.Size()
			require.NoError(t, err)
			require.NotZero(t, cdmSize)
			expSize = blockSize + walSize + cdmSize
			actSize, err = fileutil.DirSize(db.Dir())
			require.NoError(t, err)
			require.Equal(t, expSize, actSize, "registered size doesn't match actual disk size")

			// Truncate Chunk Disk Mapper and compare sizes.
			require.NoError(t, db.Head().chunkDiskMapper.Truncate(900))
			cdmSize, err = db.Head().chunkDiskMapper.Size()
			require.NoError(t, err)
			require.NotZero(t, cdmSize)
			expSize = blockSize + walSize + cdmSize
			actSize, err = fileutil.DirSize(db.Dir())
			require.NoError(t, err)
			require.Equal(t, expSize, actSize, "registered size doesn't match actual disk size")

			// Add some out of order samples to check the size of WBL.
			headApp = db.Head().AppenderV2(context.Background())
			for ts := int64(750); ts < 800; ts++ {
				_, err := headApp.Append(0, aSeries, 0, ts, float64(ts), nil, nil, storage.AOptions{})
				require.NoError(t, err)
			}
			require.NoError(t, headApp.Commit())

			walSize, err = db.Head().wal.Size()
			require.NoError(t, err)
			wblSize, err := db.Head().wbl.Size()
			require.NoError(t, err)
			require.NotZero(t, wblSize)
			cdmSize, err = db.Head().chunkDiskMapper.Size()
			require.NoError(t, err)
			expSize = blockSize + walSize + wblSize + cdmSize
			actSize, err = fileutil.DirSize(db.Dir())
			require.NoError(t, err)
			require.Equal(t, expSize, actSize, "registered size doesn't match actual disk size")

			// Decrease the max bytes limit so that a delete is triggered.
			// Check total size, total count and check that the oldest block was deleted.
			firstBlockSize := db.Blocks()[0].Size()
			sizeLimit := actSize - firstBlockSize
			db.opts.MaxBytes = sizeLimit          // Set the new db size limit one block smaller that the actual size.
			require.NoError(t, db.reloadBlocks()) // Reload the db to register the new db size.

			expBlocks := blocks[1:]
			actBlocks := db.Blocks()
			blockSize = int64(prom_testutil.ToFloat64(db.metrics.blocksBytes))
			walSize, err = db.Head().wal.Size()
			require.NoError(t, err)
			cdmSize, err = db.Head().chunkDiskMapper.Size()
			require.NoError(t, err)
			require.NotZero(t, cdmSize)
			// Expected size should take into account block size + WAL size + WBL size
			expSize = blockSize + walSize + wblSize + cdmSize
			actRetentionCount := int(prom_testutil.ToFloat64(db.metrics.sizeRetentionCount))
			actSize, err = fileutil.DirSize(db.Dir())
			require.NoError(t, err)

			require.Equal(t, 1, actRetentionCount, "metric retention count mismatch")
			require.Equal(t, expSize, actSize, "metric db size doesn't match actual disk size")
			require.LessOrEqual(t, expSize, sizeLimit, "actual size (%v) is expected to be less than or equal to limit (%v)", expSize, sizeLimit)
			require.Len(t, actBlocks, len(blocks)-1, "new block count should be decreased from:%v to:%v", len(blocks), len(blocks)-1)
			require.Equal(t, expBlocks[0].MaxTime, actBlocks[0].meta.MaxTime, "maxT mismatch of the first block")
			require.Equal(t, expBlocks[len(expBlocks)-1].MaxTime, actBlocks[len(actBlocks)-1].meta.MaxTime, "maxT mismatch of the last block")
		}
```

### Buggy: 1 (Commit: 30fecc3f2c35b1cbee29d243b3bd06fb7fb2bf2d)
**Repo**: etcd
```go
func TestClusterValidateAndAssignIDs(t *testing.T) {
	tests := []struct {
		clmembs []*Member
		membs   []*Member
		wids    []types.ID
	}{
		{
			[]*Member{
				newTestMember(1, []string{"http://127.0.0.1:2379"}, "", nil),
				newTestMember(2, []string{"http://127.0.0.2:2379"}, "", nil),
			},
			[]*Member{
				newTestMember(3, []string{"http://127.0.0.1:2379"}, "", nil),
				newTestMember(4, []string{"http://127.0.0.2:2379"}, "", nil),
			},
			[]types.ID{3, 4},
		},
	}
	for i, tt := range tests {
		lcl := newTestCluster(t, tt.clmembs)
		ecl := newTestCluster(t, tt.membs)
		if err := ValidateClusterAndAssignIDs(zaptest.NewLogger(t), lcl, ecl); err != nil {
			t.Errorf("#%d: unexpect update error: %v", i, err)
		}
		if !reflect.DeepEqual(lcl.MemberIDs(), tt.wids) {
			t.Errorf("#%d: ids = %v, want %v", i, lcl.MemberIDs(), tt.wids)
		}
	}
}
```

### Buggy: 1 (Commit: 00ba48436296e561c844a6cad325d256786df75d)
**Repo**: go
```go
func elimDeadAutosGeneric(f *ssa.Func) {
	addr := make(map[*ssa.Value]*ir.Name) // values that the address of the auto reaches
	elim := make(map[*ssa.Value]*ir.Name) // values that could be eliminated if the auto is
	move := make(map[*ir.Name]ir.NameSet) // for a (Move &y &x _) and y is unused, move[y].Add(x)
	var used ir.NameSet                   // used autos that must be kept

	// Adds a name to used and, when it is the target of a move, also
	// propagates the used state to its source.
	var usedAdd func(n *ir.Name) bool
	usedAdd = func(n *ir.Name) bool {
		if used.Has(n) {
			return false
		}
		used.Add(n)
		if s := move[n]; s != nil {
			delete(move, n)
			for n := range s {
				usedAdd(n)
			}
		}
		return true
	}

	// visit the value and report whether any of the maps are updated
	visit := func(v *ssa.Value) (changed bool) {
		args := v.Args
		switch v.Op {
		case ssaop.OpAddr, ssaop.OpLocalAddr:
			// Propagate the address if it points to an auto.
			n, ok := v.Aux.(*ir.Name)
			if !ok || (n.Class != ir.PAUTO && !isABIInternalParam(f, n)) {
				return
			}
			if addr[v] == nil {
				addr[v] = n
				changed = true
			}
			return
		case ssaop.OpVarDef:
			// v should be eliminated if we eliminate the auto.
			n, ok := v.Aux.(*ir.Name)
			if !ok || (n.Class != ir.PAUTO && !isABIInternalParam(f, n)) {
				return
			}
			if elim[v] == nil {
				elim[v] = n
				changed = true
			}
			return
		case ssaop.OpVarLive:
			// Don't delete the auto if it needs to be kept alive.

			// We depend on this check to keep the autotmp stack slots
			// for open-coded defers from being removed (since they
			// may not be used by the inline code, but will be used by
			// panic processing).
			n, ok := v.Aux.(*ir.Name)
			if !ok || (n.Class != ir.PAUTO && !isABIInternalParam(f, n)) {
				return
			}
			changed = usedAdd(n) || changed
			return
		case ssaop.OpStore, ssaop.OpMove, ssaop.OpZero:
			// v should be eliminated if we eliminate the auto.
			n, ok := addr[args[0]]
			if ok && elim[v] == nil {
				elim[v] = n
				changed = true
			}
			// Other args might hold pointers to autos.
			args = args[1:]
		}

		// The code below assumes that we have handled all the ops
		// with sym effects already. Sanity check that here.
		// Ignore Args since they can't be autos.
		if v.Op.SymEffect() != ssaop.SymNone && v.Op != ssaop.OpArg {
			panic("unhandled op with sym effect")
		}

		if v.Uses == 0 && v.Op != ssaop.OpNilCheck && !v.Op.IsCall() && !v.Op.HasSideEffects() || len(args) == 0 {
			// We need to keep nil checks even if they have no use.
			// Also keep calls and values that have side effects.
			return
		}

		// If the address of the auto reaches a memory or control
		// operation not covered above then we probably need to keep it.
		// We also need to keep autos if they reach Phis (issue #26153).
		if v.Type.IsMemory() || v.Type.IsFlags() || v.Op == ssaop.OpPhi || v.MemoryArg() != nil {
			for _, a := range args {
				if n, ok := addr[a]; ok {
					// If the addr of n is used by an OpMove as its source arg,
					// and the OpMove's target arg is the addr of a unused name,
					// then temporarily treat n as unused, and record in move map.
					if nam, ok := elim[v]; ok && v.Op == ssaop.OpMove && !used.Has(nam) {
						if used.Has(n) {
							continue
						}
						s := move[nam]
						if s == nil {
							s = ir.NameSet{}
							move[nam] = s
						}
						s.Add(n)
						continue
					}
					changed = usedAdd(n) || changed
				}
			}
			return
		}

		// Propagate any auto addresses through v.
		var node *ir.Name
		for _, a := range args {
			if n, ok := addr[a]; ok {
				if node == nil {
					if !used.Has(n) {
						node = n
					}
				} else {
					if node == n {
						continue
					}
					// Most of the time we only see one pointer
					// reaching an op, but some ops can take
					// multiple pointers (e.g. NeqPtr, Phi etc.).
					// This is rare, so just propagate the first
					// value to keep things simple.
					changed = usedAdd(n) || changed
				}
			}
		}
		if node == nil {
			return
		}
		if addr[v] == nil {
			// The address of an auto reaches this op.
			addr[v] = node
			changed = true
			return
		}
		if addr[v] != node {
			// This doesn't happen in practice, but catch it just in case.
			changed = usedAdd(node) || changed
		}
		return
	}

	iterations := 0
	for {
		if iterations == 4 {
			// give up
			return
		}
		iterations++
		changed := false
		for _, b := range f.Blocks {
			for _, v := range b.Values {
				changed = visit(v) || changed
			}
			// keep the auto if its address reaches a control value
			for _, c := range b.ControlValues() {
				if n, ok := addr[c]; ok {
					changed = usedAdd(n) || changed
				}
			}
		}
		if !changed {
			break
		}
	}

	// Eliminate stores to unread autos.
	for v, n := range elim {
		if used.Has(n) {
			continue
		}
		// replace with OpCopy
		v.SetArgs1(v.MemoryArg())
		v.Aux = nil
		v.AuxInt = 0
		v.Op = ssaop.OpCopy
	}
}
```

### Buggy: 1 (Commit: 234a6d4c00cb77af9852aca0b8289745d5529b4b)
**Repo**: gin
```go
func(w http.ResponseWriter, r *http.Request) {
		writer := &responseWriter{}
		writer.reset(w)

		writer.WriteHeader(http.StatusInternalServerError)
		writer.Flush()
	}
```

### Buggy: 1 (Commit: cdb3c1fc8930899c920578bb987788a5c9131157)
**Repo**: terraform
```go
func(req providers.ApplyResourceChangeRequest) (resp providers.ApplyResourceChangeResponse) {
		// only cancel once
		once.Do(func() {
			shutdownCh <- struct{}{}
		})

		// Because of the internal lock in the MockProvider, we can't
		// coordiante directly with the calling of Stop, and making the
		// MockProvider concurrent is disruptive to a lot of existing tests.
		// Wait here a moment to help make sure the main goroutine gets to the
		// Stop call before we exit, or the plan may finish before it can be
		// canceled.
		time.Sleep(200 * time.Millisecond)

		resp.NewState = req.PlannedState
		return
	}
```

### Buggy: 0 (Commit: cdb3c1fc8930899c920578bb987788a5c9131157)
**Repo**: terraform
```go
func checkGoldenReferenceHumanOutput(t *testing.T, output *terminal.TestOutput, fixturePathName string) {
	t.Helper()

	// No params
	checkParameterizedGoldenReferenceHumanOutput(t, output, fixturePathName)
}
```

### Buggy: 0 (Commit: cb1e5f49d59799a7ea7637fa5b7bfc2c89dffd75)
**Repo**: go
```go
func TestEnsurePipelineContains(t *testing.T) {
	tests := []struct {
		input, output string
		ids           []string
	}{
		{
			"{{.X}}",
			".X",
			[]string{},
		},
		{
			"{{.X | html}}",
			".X | html",
			[]string{},
		},
		{
			"{{.X}}",
			".X | html",
			[]string{"html"},
		},
		{
			"{{html .X}}",
			"_eval_args_ .X | html | urlquery",
			[]string{"html", "urlquery"},
		},
		{
			"{{html .X .Y .Z}}",
			"_eval_args_ .X .Y .Z | html | urlquery",
			[]string{"html", "urlquery"},
		},
		{
			"{{.X | print}}",
			".X | print | urlquery",
			[]string{"urlquery"},
		},
		{
			"{{.X | print | urlquery}}",
			".X | print | urlquery",
			[]string{"urlquery"},
		},
		{
			"{{.X | urlquery}}",
			".X | html | urlquery",
			[]string{"html", "urlquery"},
		},
		{
			"{{.X | print 2 | .f 3}}",
			".X | print 2 | .f 3 | urlquery | html",
			[]string{"urlquery", "html"},
		},
		{
			// covering issue 10801
			"{{.X | println.x }}",
			".X | println.x | urlquery | html",
			[]string{"urlquery", "html"},
		},
		{
			// covering issue 10801
			"{{.X | (print 12 | println).x }}",
			".X | (print 12 | println).x | urlquery | html",
			[]string{"urlquery", "html"},
		},
		// The following test cases ensure that the merging of internal escapers
		// with the predefined "html" and "urlquery" escapers is correct.
		{
			"{{.X | urlquery}}",
			".X | _html_template_urlfilter | urlquery",
			[]string{"_html_template_urlfilter", "_html_template_urlnormalizer"},
		},
		{
			"{{.X | urlquery}}",
			".X | urlquery | _html_template_urlfilter | _html_template_cssescaper",
			[]string{"_html_template_urlfilter", "_html_template_cssescaper"},
		},
		{
			"{{.X | urlquery}}",
			".X | urlquery",
			[]string{"_html_template_urlnormalizer"},
		},
		{
			"{{.X | urlquery}}",
			".X | urlquery",
			[]string{"_html_template_urlescaper"},
		},
		{
			"{{.X | html}}",
			".X | html",
			[]string{"_html_template_htmlescaper"},
		},
		{
			"{{.X | html}}",
			".X | html",
			[]string{"_html_template_rcdataescaper"},
		},
	}
	for i, test := range tests {
		tmpl := template.Must(template.New("test").Parse(test.input))
		action, ok := (tmpl.Tree.Root.Nodes[0].(*parse.ActionNode))
		if !ok {
			t.Errorf("First node is not an action: %s", test.input)
			continue
		}
		pipe := action.Pipe
		originalIDs := make([]string, len(test.ids))
		copy(originalIDs, test.ids)
		ensurePipelineContains(pipe, test.ids)
		got := pipe.String()
		if got != test.output {
			t.Errorf("#%d: %s, %v: want\n\t%s\ngot\n\t%s", i, test.input, originalIDs, test.output, got)
		}
	}
}
```

### Buggy: 1 (Commit: 4d628bbdc3441f3c44b1f6f4e6ad04f4df4728bf)
**Repo**: hugo
```go
func ConvertIfPossible(val reflect.Value, typ reflect.Type) (reflect.Value, bool) {
	switch val.Kind() {
	case reflect.Pointer, reflect.Interface:
		if val.IsNil() {
			// Return typ's zero value.
			return reflect.Zero(typ), true
		}
		val = val.Elem()
	}

	if val.Type().AssignableTo(typ) {
		// No conversion needed.
		return val, true
	}

	if IsInt(typ.Kind()) {
		return convertToIntIfPossible(val, typ)
	}
	if IsFloat(typ.Kind()) {
		return convertToFloatIfPossible(val, typ)
	}
	if IsUint(typ.Kind()) {
		return convertToUintIfPossible(val, typ)
	}
	if IsString(typ.Kind()) && IsString(val.Kind()) {
		return val.Convert(typ), true
	}

	return reflect.Value{}, false
}
```

### Buggy: 1 (Commit: 70a2b4871356c35d1638de047db3a4a780b2eec3)
**Repo**: etcd
```go
func (s *EtcdServer) Txn(ctx context.Context, r *pb.TxnRequest) (*pb.TxnResponse, error) {
	readOnly := txn.IsTxnReadonly(r)

	var span trace.Span
	ctx, span = traceutil.Tracer.Start(ctx, "txn", trace.WithAttributes(
		attribute.String("compare_first_key", firstCompareKey(r.GetCompare())),
		attribute.String("success_first_key", firstOpKey(r.GetSuccess())),
		attribute.String("success_first_type", firstOpType(r.GetSuccess())),
		attribute.Int64("success_first_lease", firstOpLease(r.GetSuccess())),
		attribute.Int("compare_len", len(r.GetCompare())),
		attribute.Int("success_len", len(r.GetSuccess())),
		attribute.Int("failure_len", len(r.GetFailure())),
		attribute.Bool("read_only", readOnly),
	))
	defer span.End()

	ctx, trace := traceutil.EnsureTrace(ctx, s.Logger(), "transaction",
		traceutil.Field{Key: "read_only", Value: readOnly},
	)
	if readOnly {
		if !txn.IsTxnSerializable(r) {
			err := s.read.LinearizableReadNotify(ctx)
			trace.Step("agreement among raft nodes before linearized reading")
			if err != nil {
				return nil, err
			}
		}
		var resp *pb.TxnResponse
		var err error
		chk := func(ai *auth.AuthInfo) error {
			return apply2.CheckTxnAuth(s.authStore, ai, r)
		}

		defer func(start time.Time) {
			txn.WarnOfExpensiveReadOnlyTxnRequest(s.Logger(), s.Cfg.WarningApplyDuration, start, r, resp, err)
			trace.LogIfLong(traceThreshold)
			success := err == nil
			requestDurationSec.WithLabelValues("ReadonlyTxn", strconv.FormatBool(success)).Observe(time.Since(start).Seconds())
		}(time.Now())

		get := func() {
			resp, _, err = txn.Txn(ctx, s.Logger(), r, s.Cfg.ServerFeatureGate.Enabled(features.TxnModeWriteWithSharedBuffer), s.KV(), s.lessor)
		}
		if serr := s.doSerialize(ctx, chk, get); serr != nil {
			return nil, serr
		}
		return resp, err
	}

	ctx = context.WithValue(ctx, traceutil.StartTimeKey{}, time.Now())
	resp, err := s.raftRequest(ctx, pb.InternalRaftRequest{Txn: r})
	if err != nil {
		return nil, err
	}
	return resp.(*pb.TxnResponse), nil
}
```

### Buggy: 0 (Commit: 887c8486d36f13ebf2ae731d1ed9901a3673ee71)
**Repo**: etcd
```go
func isConnectedSince(transport rafthttp.Transporter, since time.Time, remote types.ID) bool {
	t := transport.ActiveSince(remote)
	return !t.IsZero() && t.Before(since)
}
```

### Buggy: 0 (Commit: 03847224e1581cd6c467048cc7f90697fb101cdb)
**Repo**: terraform
```go
func TestContext2Apply_basic(t *testing.T) {
	m := testModule(t, "apply-good")
	p := testProvider("aws")
	p.PlanResourceChangeFn = testDiffFn
	p.ApplyResourceChangeFn = testApplyFn
	ctx := testContext2(t, &ContextOpts{
		Providers: map[addrs.Provider]providers.Factory{
			addrs.NewDefaultProvider("aws"): testProviderFuncFixed(p),
		},
	})

	plan, diags := ctx.Plan(m, states.NewState(), DefaultPlanOpts)
	tfdiags.AssertNoErrors(t, diags)

	state, diags := ctx.Apply(plan, m, nil)
	if diags.HasErrors() {
		t.Fatalf("diags: %s", diags.Err())
	}

	mod := state.RootModule()
	if len(mod.Resources) < 2 {
		t.Fatalf("bad: %#v", mod.Resources)
	}

	actual := strings.TrimSpace(state.String())
	expected := strings.TrimSpace(testTerraformApplyStr)
	if actual != expected {
		t.Fatalf("wrong result\n\ngot:\n%s\n\nwant:\n%s", actual, expected)
	}
}
```

### Buggy: 1 (Commit: 8ce57d8d14aff2f4c9b5a0a1ec966bf899c25c6f)
**Repo**: kubernetes
```go
func(t *testing.T) {
			// For some asynchronous implementations of storage interface (in particular watchcache),
			// certain requests may impact result of further requests. As an example, if we first
			// ensure that watchcache is synchronized up to ResourceVersion X (using Get/List requests
			// with NotOlderThan semantic), the further requests (even specifying earlier resource
			// version) will also return the result synchronized to at least ResourceVersion X.
			// By parallelizing test cases we ensure that the order in which test cases are defined
			// doesn't automatically preclude some scenarios from happening.
			t.Parallel()

			out := &example.Pod{}
			err := store.Get(ctx, tt.key, storage.GetOptions{IgnoreNotFound: tt.ignoreNotFound, ResourceVersion: tt.rv}, out)
			if tt.expectedErrFunc != nil {
				expectedErr := tt.expectedErrFunc()
				assert.Equal(t, expectedErr, err)
				return
			}
			if tt.expectNotFoundErr {
				if err == nil || !storage.IsNotFound(err) {
					t.Errorf("expecting not found error, but get: %v", err)
				}
				return
			}
			if tt.expectRVTooLarge {
				if err == nil || !storage.IsTooLargeResourceVersion(err) {
					t.Errorf("expecting resource version too high error, but get: %v", err)
				}
				return
			}
			if err != nil {
				t.Fatalf("Get failed: %v", err)
			}

			if tt.expectedAlternatives == nil {
				expectNoDiff(t, fmt.Sprintf("%s: incorrect pod", tt.name), tt.expectedOut, out)
			} else {
				ExpectContains(t, fmt.Sprintf("%s: incorrect pod", tt.name), toInterfaceSlice(tt.expectedAlternatives), out)
			}
		}
```

### Buggy: 1 (Commit: c4287b1300363cb3dc2c8408299d3ba6deded485)
**Repo**: gin
```go
func TestContextNegotiationFormatCustom(t *testing.T) {
	c, _ := CreateTestContext(httptest.NewRecorder())
	c.Request, _ = http.NewRequest(http.MethodPost, "/", nil)
	c.Request.Header.Add("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9;q=0.8")

	c.Accepted = nil
	c.SetAccepted(MIMEJSON, MIMEXML)

	assert.Equal(t, MIMEJSON, c.NegotiateFormat(MIMEJSON, MIMEXML))
	assert.Equal(t, MIMEXML, c.NegotiateFormat(MIMEXML, MIMEHTML))
	assert.Equal(t, MIMEJSON, c.NegotiateFormat(MIMEJSON))
}
```

### Buggy: 0 (Commit: cb6a7072230920fb47ece28f67501a2c15934ade)
**Repo**: hugo
```go
func (d Decoder) UnmarshalStringTo(data string, typ any) (any, error) {
	data = strings.TrimSpace(data)
	// We only check for the possible types in YAML, JSON and TOML.
	switch typ.(type) {
	case string:
		return data, nil
	case map[string]any, hmaps.Params:
		format := d.FormatFromContentString(data)
		return d.UnmarshalToMap([]byte(data), format)
	case []any:
		// A standalone slice. Let YAML handle it.
		return d.Unmarshal([]byte(data), YAML)
	case bool:
		return cast.ToBoolE(data)
	case int:
		return cast.ToIntE(data)
	case int64:
		return cast.ToInt64E(data)
	case float64:
		return cast.ToFloat64E(data)
	default:
		return nil, fmt.Errorf("unmarshal: %T not supported", typ)
	}
}
```

### Buggy: 1 (Commit: cb6a7072230920fb47ece28f67501a2c15934ade)
**Repo**: hugo
```go
func (p *PagesFromTemplate) Execute(ctx context.Context) (BuildInfo, error) {
	defer func() {
		p.buildState.PrepareNextBuild()
	}()

	f, err := p.GoTmplFi.Meta().Open()
	if err != nil {
		return BuildInfo{}, err
	}
	defer f.Close()

	tmpl, err := p.TemplateStore.TextParse(p.GoTmplFi.Meta().PathInfo.Path(), helpers.ReaderToString(f))
	if err != nil {
		return BuildInfo{}, err
	}

	data := &pagesFromDataTemplateContext{
		p: p,
	}

	ctx = tpl.Context.DependencyManagerScopedProvider.Set(ctx, p)

	if err := p.TemplateStore.ExecuteWithContext(ctx, tmpl, io.Discard, data); err != nil {
		return BuildInfo{}, err
	}

	if p.Watching {
		p.buildState.resolveDeletedPaths()
	}

	bi := BuildInfo{
		NumPagesAdded:       p.buildState.NumPagesAdded,
		NumResourcesAdded:   p.buildState.NumResourcesAdded,
		EnableAllLanguages:  p.buildState.EnableAllLanguages,
		EnableAllDimensions: p.buildState.EnableAllDimensions,
		ChangedIdentities:   p.buildState.ChangedIdentities,
		DeletedPaths:        p.buildState.DeletedPaths,
		Path:                p.GoTmplFi.Meta().PathInfo,
	}

	return bi, nil
}
```

### Buggy: 1 (Commit: 03847224e1581cd6c467048cc7f90697fb101cdb)
**Repo**: terraform
```go
func versionHelper(expr hcl.Expression) (configs.VersionConstraint, hcl.Diagnostics) {
	var diags hcl.Diagnostics
	var versionRaw string

	ret := configs.VersionConstraint{
		DeclRange: expr.Range(),
	}

	valDiags := gohcl.DecodeExpression(expr, nil, &versionRaw)
	diags = append(diags, valDiags...)
	if !valDiags.HasErrors() {
		constraints, err := version.NewConstraint(versionRaw)
		if err != nil {
			// NewConstraint doesn't return user-friendly errors, so we'll just
			// ignore the provided error and produce our own generic one.
			diags = append(diags, &hcl.Diagnostic{
				Severity: hcl.DiagError,
				Summary:  "Invalid version constraint",
				Detail:   "This string does not use correct version constraint syntax.", // Not very actionable :(
				Subject:  expr.Range().Ptr(),
			})
			return ret, diags
		}
		ret.Required = constraints
	}

	return ret, diags
}
```

### Buggy: 1 (Commit: 627bd61358a596b80dcc73581eb2d5311386eed3)
**Repo**: kubernetes
```go
func NewTypedStorageClassInformerWithOptions(client kubernetes.Interface, options internalinterfaces.InformerOptions) StorageClassIndexInformer {
	gvr := schema.GroupVersionResource{Group: "storage.k8s.io", Version: "v1beta1", Resource: "storageclasss"}
	identifier := options.InformerName.WithResource(gvr)
	tweakListOptions := options.TweakListOptions
	return cache.NewTypedSharedIndexInformer[*apistoragev1beta1.StorageClass](cache.NewSharedIndexInformerWithOptions(
		cache.ToListWatcherWithWatchListSemantics(&cache.ListWatch{
			ListFunc: func(opts v1.ListOptions) (runtime.Object, error) {
				if tweakListOptions != nil {
					tweakListOptions(&opts)
				}
				return client.StorageV1beta1().StorageClasses().List(context.Background(), opts)
			},
			WatchFunc: func(opts v1.ListOptions) (watch.Interface, error) {
				if tweakListOptions != nil {
					tweakListOptions(&opts)
				}
				return client.StorageV1beta1().StorageClasses().Watch(context.Background(), opts)
			},
			ListWithContextFunc: func(ctx context.Context, opts v1.ListOptions) (runtime.Object, error) {
				if tweakListOptions != nil {
					tweakListOptions(&opts)
				}
				return client.StorageV1beta1().StorageClasses().List(ctx, opts)
			},
			WatchFuncWithContext: func(ctx context.Context, opts v1.ListOptions) (watch.Interface, error) {
				if tweakListOptions != nil {
					tweakListOptions(&opts)
				}
				return client.StorageV1beta1().StorageClasses().Watch(ctx, opts)
			},
		}, client),
		&apistoragev1beta1.StorageClass{},
		cache.SharedIndexInformerOptions{
			ResyncPeriod: options.ResyncPeriod,
			Indexers:     options.Indexers,
			Identifier:   identifier,
		},
	))
}
```

### Buggy: 1 (Commit: e582f3f2077d54e8edf654248ee53372b7f847c6)
**Repo**: etcd
```go
func (m *Metadata) GetNodeID() uint64 {
	if m != nil {
		return m.NodeID
	}
	return 0
}
```

### Buggy: 0 (Commit: ce2c6606ea030e694d8d5eb3717deceefbb3a40f)
**Repo**: go
```go
func(_ []string, a Attr) Attr { return Attr{} }
```

### Buggy: 1 (Commit: ae543a5877522a51b08be4c74ed52ee38a175151)
**Repo**: prometheus
```go
func (p *OpenMetrics2Parser) parseExemplars() error {
	for {
		done, err := p.parseSingleExemplar()
		if err != nil {
			return err
		}
		if done {
			// tLinebreak was consumed inside parseSingleExemplar.
			return nil
		}
		// tComment was consumed; another exemplar follows.
	}
}
```

### Buggy: 1 (Commit: 8aefeda22f7cbc7050e72d44e4bf3398dffeec33)
**Repo**: terraform
```go
func(i, j int) bool {
			return policies[i].PolicyMetadata.PolicyName < policies[j].PolicyMetadata.PolicyName
		}
```

### Buggy: 1 (Commit: 6b3ba3a7e22ae2809605b8118aeed08b244f1955)
**Repo**: hugo
```go
func() (any, error) { return ns.Intersect([]int64{a}, []int{int(a)}) }
```

### Buggy: 1 (Commit: d441ad6dc1b51c2a93e5ef0ef4a8594fc8166e56)
**Repo**: etcd
```go
func NewTmpWAL(tb testing.TB, reqs []etcdserverpb.InternalRaftRequest) (*wal.WAL, string) {
	tb.Helper()
	dir, err := os.MkdirTemp(tb.TempDir(), "etcd_wal_test")
	if err != nil {
		panic(err)
	}
	tmpPath := filepath.Join(dir, "wal")
	lg := zaptest.NewLogger(tb)
	w, err := wal.Create(lg, tmpPath, nil)
	if err != nil {
		tb.Fatalf("Failed to create WAL: %v", err)
	}
	err = w.Close()
	if err != nil {
		tb.Fatalf("Failed to close WAL: %v", err)
	}
	if len(reqs) != 0 {
		w, err = wal.Open(lg, tmpPath, walpb.Snapshot{})
		if err != nil {
			tb.Fatalf("Failed to open WAL: %v", err)
		}

		var state raftpb.HardState
		_, state, _, err = w.ReadAll()
		if err != nil {
			tb.Fatalf("Failed to read WAL: %v", err)
		}
		var entries []raftpb.Entry
		for _, req := range reqs {
			entries = append(entries, raftpb.Entry{
				Term:  1,
				Index: 1,
				Type:  raftpb.EntryNormal,
				Data:  pbutil.MustMarshal(&req),
			})
		}
		err = w.Save(state, entries)
		if err != nil {
			tb.Fatalf("Failed to save WAL: %v", err)
		}
		err = w.Close()
		if err != nil {
			tb.Fatalf("Failed to close WAL: %v", err)
		}
	}

	w, err = wal.OpenForRead(lg, tmpPath, walpb.Snapshot{})
	if err != nil {
		tb.Fatalf("Failed to open WAL: %v", err)
	}
	return w, tmpPath
}
```

### Buggy: 1 (Commit: 740fcaabb9e2ee54b2575ad04bd308a87cc3c406)
**Repo**: go
```go
func (x Int32s) Mul(y Int32s) Int32s
```

### Buggy: 1 (Commit: 819eab448b0057a95aecee06fed08c2e05270b32)
**Repo**: go
```go
func (f *Fetcher) download(ctx context.Context, mod module.Version) (dir string, err error) {
	ctx, span := trace.StartSpan(ctx, "modfetch.download "+mod.String())
	defer span.Done()

	dir, err = DownloadDir(ctx, mod)
	if err == nil {
		// The directory has already been completely extracted (no .partial file exists).
		return dir, nil
	} else if dir == "" || !errors.Is(err, fs.ErrNotExist) {
		return "", err
	}

	// To avoid cluttering the cache with extraneous files,
	// DownloadZip uses the same lockfile as Download.
	// Invoke DownloadZip before locking the file.
	zipfile, err := f.DownloadZip(ctx, mod)
	if err != nil {
		return "", err
	}

	return unzip(ctx, mod, zipfile)
}
```

### Buggy: 0 (Commit: 522ebc8370421796f13715117803d3302e8b61bd)
**Repo**: go
```go
func asNamed(t Type) *Named {
	n, _ := Unalias(t).(*Named)
	return n
}
```

### Buggy: 0 (Commit: 77e0c9e6af13d3affc136a14b000f3f9c3fc5a3c)
**Repo**: terraform
```go
func (d *Deferred) ReportModuleExpansionDeferred(addr addrs.PartialExpandedModule) {
	d.mu.Lock()
	defer d.mu.Unlock()

	if d.partialExpandedModulesDeferred.Has(addr) {
		// This indicates a bug in the caller, since our graph walk should
		// ensure that we visit and evaluate each distinct partial-expanded
		// prefix only once.
		panic(fmt.Sprintf("duplicate deferral report for %s", addr))
	}
	d.partialExpandedModulesDeferred.Add(addr)
}
```

### Buggy: 1 (Commit: f254afa6f14871d9278670d63ccdab08908d5423)
**Repo**: etcd
```go
func TestEnableAuth(t *testing.T) {
	tdir := t.TempDir()
	cfg := NewConfig()
	cfg.Dir = tdir
	e, err := StartEtcd(cfg)
	if err != nil {
		t.Fatal(err)
	}
	defer e.Close()
	client := v3client.New(e.Server)
	defer client.Close()

	_, err = client.RoleAdd(t.Context(), "root")
	if err != nil {
		t.Fatal(err)
	}
	_, err = client.UserAdd(t.Context(), "root", "root")
	if err != nil {
		t.Fatal(err)
	}
	_, err = client.UserGrantRole(t.Context(), "root", "root")
	if err != nil {
		t.Fatal(err)
	}
	_, err = client.AuthEnable(t.Context())
	if err != nil {
		t.Fatal(err)
	}
}
```

### Buggy: 1 (Commit: cb6a7072230920fb47ece28f67501a2c15934ade)
**Repo**: hugo
```go
func(t *testing.T) {
		b := hugolib.TestRunning(t, createFiles(t))

		b.AssertFileContent("public/index.html",
			"idPart: Format: int8|$",
		)

		// Rebuild triggered by remote polling.
		time.Sleep(800 * time.Millisecond)

		b.AssertFileContent("public/index.html",
			"idPart: Format: int16|$",
		)
	}
```

### Buggy: 0 (Commit: 30fecc3f2c35b1cbee29d243b3bd06fb7fb2bf2d)
**Repo**: etcd
```go
func TestClusterValidateConfigurationChangeV3(t *testing.T) {
	cl := NewCluster(zaptest.NewLogger(t), WithMaxLearners(1))
	be := newMembershipBackend()
	cl.SetBackend(be)
	for i := 1; i <= 4; i++ {
		var isLearner bool
		if i == 1 {
			isLearner = true
		}
		attr := RaftAttributes{PeerURLs: []string{fmt.Sprintf("http://127.0.0.1:%d", i)}, IsLearner: isLearner}
		cl.AddMember(&Member{ID: types.ID(i), RaftAttributes: attr}, true)
	}
	cl.RemoveMember(4, true)

	attr := RaftAttributes{PeerURLs: []string{fmt.Sprintf("http://127.0.0.1:%d", 1)}}
	ctx, err := json.Marshal(&Member{ID: types.ID(5), RaftAttributes: attr})
	if err != nil {
		t.Fatal(err)
	}

	attr = RaftAttributes{PeerURLs: []string{fmt.Sprintf("http://127.0.0.1:%d", 1)}}
	ctx1, err := json.Marshal(&Member{ID: types.ID(1), RaftAttributes: attr})
	if err != nil {
		t.Fatal(err)
	}

	attr = RaftAttributes{PeerURLs: []string{fmt.Sprintf("http://127.0.0.1:%d", 5)}}
	ctx5, err := json.Marshal(&Member{ID: types.ID(5), RaftAttributes: attr})
	if err != nil {
		t.Fatal(err)
	}

	attr = RaftAttributes{PeerURLs: []string{fmt.Sprintf("http://127.0.0.1:%d", 3)}}
	ctx2to3, err := json.Marshal(&Member{ID: types.ID(2), RaftAttributes: attr})
	if err != nil {
		t.Fatal(err)
	}

	attr = RaftAttributes{PeerURLs: []string{fmt.Sprintf("http://127.0.0.1:%d", 5)}}
	ctx2to5, err := json.Marshal(&Member{ID: types.ID(2), RaftAttributes: attr})
	if err != nil {
		t.Fatal(err)
	}

	ctx3, err := json.Marshal(&ConfigChangeContext{Member: Member{ID: types.ID(3), RaftAttributes: attr}, IsPromote: true})
	if err != nil {
		t.Fatal(err)
	}

	ctx6, err := json.Marshal(&ConfigChangeContext{Member: Member{ID: types.ID(6), RaftAttributes: attr}, IsPromote: true})
	if err != nil {
		t.Fatal(err)
	}

	attr = RaftAttributes{PeerURLs: []string{fmt.Sprintf("http://127.0.0.1:%d", 7)}, IsLearner: true}
	ctx7, err := json.Marshal(&ConfigChangeContext{Member: Member{ID: types.ID(7), RaftAttributes: attr}})
	if err != nil {
		t.Fatal(err)
	}

	attr = RaftAttributes{PeerURLs: []string{fmt.Sprintf("http://127.0.0.1:%d", 1)}, IsLearner: true}
	ctx8, err := json.Marshal(&ConfigChangeContext{Member: Member{ID: types.ID(1), RaftAttributes: attr}, IsPromote: true})
	if err != nil {
		t.Fatal(err)
	}
	tests := []struct {
		cc   raftpb.ConfChange
		werr error
	}{
		{
			raftpb.ConfChange{
				Type:   raftpb.ConfChangeRemoveNode,
				NodeID: 3,
			},
			nil,
		},
		{
			raftpb.ConfChange{
				Type:   raftpb.ConfChangeAddNode,
				NodeID: 4,
			},
			ErrIDRemoved,
		},
		{
			raftpb.ConfChange{
				Type:   raftpb.ConfChangeRemoveNode,
				NodeID: 4,
			},
			ErrIDRemoved,
		},
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeAddNode,
				NodeID:  1,
				Context: ctx1,
			},
			ErrIDExists,
		},
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeAddNode,
				NodeID:  5,
				Context: ctx,
			},
			ErrPeerURLexists,
		},
		{
			raftpb.ConfChange{
				Type:   raftpb.ConfChangeRemoveNode,
				NodeID: 5,
			},
			ErrIDNotFound,
		},
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeAddNode,
				NodeID:  5,
				Context: ctx5,
			},
			nil,
		},
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeUpdateNode,
				NodeID:  5,
				Context: ctx,
			},
			ErrIDNotFound,
		},
		// try to change the peer url of 2 to the peer url of 3
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeUpdateNode,
				NodeID:  2,
				Context: ctx2to3,
			},
			ErrPeerURLexists,
		},
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeUpdateNode,
				NodeID:  2,
				Context: ctx2to5,
			},
			nil,
		},
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeAddNode,
				NodeID:  3,
				Context: ctx3,
			},
			ErrMemberNotLearner,
		},
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeAddNode,
				NodeID:  6,
				Context: ctx6,
			},
			ErrIDNotFound,
		},
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeAddLearnerNode,
				NodeID:  7,
				Context: ctx7,
			},
			ErrTooManyLearners,
		},
		{
			raftpb.ConfChange{
				Type:    raftpb.ConfChangeAddNode,
				NodeID:  1,
				Context: ctx8,
			},
			nil,
		},
	}
	for i, tt := range tests {
		err := cl.ValidateConfigurationChange(tt.cc, true)
		if !errors.Is(err, tt.werr) {
			t.Errorf("#%d: validateConfigurationChange error = %v, want %v", i, err, tt.werr)
		}
	}
}
```

### Buggy: 0 (Commit: 627bd61358a596b80dcc73581eb2d5311386eed3)
**Repo**: kubernetes
```go
func(opts metav1.ListOptions) (runtime.Object, error) {
				if tweakListOptions != nil {
					tweakListOptions(&opts)
				}
				return client.StorageV1().StorageClasses().List(context.Background(), opts)
			}
```

### Buggy: 0 (Commit: 99d006e6c20e156e0e925fd87bd94816e2f8e9cb)
**Repo**: prometheus
```go
func (db *DB) gc(mint int64) {
	deleted := db.series.GC(mint, db.opts.CheckpointFromInMemorySeries)
	db.metrics.numActiveSeries.Sub(float64(len(deleted)))

	_, last, _ := wlog.Segments(db.wal.Dir())

	// We want to keep series records for any newly deleted series
	// until we've passed the last recorded segment. This prevents
	// the WAL having samples for series records that no longer exist.
	for ref, lset := range deleted {
		db.deleted[ref] = deletedRefMeta{lastSegment: last, labels: lset}
	}

	db.metrics.numWALSeriesPendingDeletion.Set(float64(len(db.deleted)))
}
```

### Buggy: 0 (Commit: 07b9fba11ba4e781ee87ecca56e78bde5775950c)
**Repo**: hugo
```go
func (c *hugoBuilder) doWithPublishDirs(f func(sourceFs *filesystems.SourceFilesystem) (uint64, error)) (map[string]uint64, error) {
	langCount := make(map[string]uint64)

	h, err := c.hugo()
	if err != nil {
		return nil, err
	}
	staticFilesystems := h.BaseFs.SourceFilesystems.Static

	if len(staticFilesystems) == 0 {
		c.r.logger.Infoln("No static directories found to sync")
		return langCount, nil
	}

	for lang, fs := range staticFilesystems {
		cnt, err := f(fs)
		if err != nil {
			return langCount, err
		}
		if lang == "" {
			// Not multihost
			c.withConf(func(conf *commonConfig) {
				for _, l := range conf.configs.Languages {
					langCount[l.Lang] = cnt
				}
			})
		} else {
			langCount[lang] = cnt
		}
	}

	return langCount, nil
}
```

### Buggy: 1 (Commit: 7cc858aed0b8fc42d9e5ab02a7abb4b533f8772f)
**Repo**: etcd
```go
func TestParseCompare(t *testing.T) {
	tests := []struct {
		name       string
		line       string
		wantResult pb.Compare_CompareResult
		wantLease  int64
		wantErr    bool
	}{
		{
			name:       "issue 20773 regression",
			line:       `lease("foo1") > "0"`,
			wantResult: pb.Compare_GREATER,
			wantLease:  0,
		},
		{
			name:       "hex lease lowercase",
			line:       `lease("foo1") = "f"`,
			wantResult: pb.Compare_EQUAL,
			wantLease:  15,
		},
		{
			name:       "hex lease uppercase",
			line:       `lease("foo1") = "AF"`,
			wantResult: pb.Compare_EQUAL,
			wantLease:  175,
		},
		{
			name:       "long lease id from etcdctl output",
			line:       `lease("foo1") = "2d8257079fa1bc0c"`,
			wantResult: pb.Compare_EQUAL,
			wantLease:  3279279168933706764,
		},
		{
			name:    "invalid hex character",
			line:    `lease("foo1") > "g"`,
			wantErr: true,
		},
		{
			name:    "overflow int64 range",
			line:    `lease("foo1") > "ffffffffffffffff"`,
			wantErr: true,
		},
		{
			name:    "missing quoted lease value",
			line:    `lease("foo1") > 10`,
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			cmp, err := ParseCompare(tt.line)
			if tt.wantErr {
				require.Error(t, err)
				return
			}

			require.NoError(t, err)
			require.Equal(t, []byte("foo1"), cmp.Key)
			require.Equal(t, pb.Compare_LEASE, cmp.Target)
			require.Equal(t, tt.wantResult, cmp.Result)

			leaseCmp, ok := cmp.TargetUnion.(*pb.Compare_Lease)
			require.True(t, ok)
			require.Equal(t, tt.wantLease, leaseCmp.Lease)
		})
	}
}
```

### Buggy: 1 (Commit: d75fcd4c9ab260e5225de590f1f0f8c0e0e12d11)
**Repo**: gin
```go
func (w *responseWriter) CloseNotify() <-chan bool {
	return w.ResponseWriter.(http.CloseNotifier).CloseNotify()
}
```

### Buggy: 1 (Commit: d6718ce9a00ff1633dc6569b210678ed92ddcf0a)
**Repo**: terraform
```go
func decodeRequiredProvidersBlock(block *hcl.Block) (
	*RequiredProviders,
	map[string]*ProviderRequirementExpr,
	hcl.Diagnostics,
) {
	attrs, diags := block.Body.JustAttributes()
	if diags.HasErrors() {
		return nil, nil, diags
	}

	ret := &RequiredProviders{
		RequiredProviders: make(map[string]*RequiredProvider),
		DeclRange:         block.DefRange,
	}
	var deferredExprs map[string]*ProviderRequirementExpr

	for name, attr := range attrs {
		rp := &RequiredProvider{
			Name:      name,
			DeclRange: attr.Expr.Range(),
		}

		// Look for a single static string, in case we have the legacy version-only
		// format in the configuration.
		if expr, err := attr.Expr.Value(nil); err == nil && expr.Type().IsPrimitiveType() {
			vc, reqDiags := decodeVersionConstraint(attr)
			diags = append(diags, reqDiags...)

			pType, err := addrs.ParseProviderPart(rp.Name)
			if err != nil {
				diags = append(diags, &hcl.Diagnostic{
					Severity: hcl.DiagError,
					Summary:  "Invalid provider name",
					Detail:   err.Error(),
					Subject:  attr.Expr.Range().Ptr(),
				})
				continue
			}

			rp.Requirement = vc
			rp.Type = addrs.ImpliedProviderForUnqualifiedType(pType)
			ret.RequiredProviders[name] = rp

			continue
		}

		// verify that the local name is already localized or produce an error.
		nameDiags := checkProviderNameNormalized(name, attr.Expr.Range())
		if nameDiags.HasErrors() {
			diags = append(diags, nameDiags...)
			continue
		}

		kvs, mapDiags := hcl.ExprMap(attr.Expr)
		if mapDiags.HasErrors() {
			diags = append(diags, &hcl.Diagnostic{
				Severity: hcl.DiagError,
				Summary:  "Invalid required_providers object",
				Detail:   "required_providers entries must be strings or objects.",
				Subject:  attr.Expr.Range().Ptr(),
			})
			continue
		}

		providerExpr := &ProviderRequirementExpr{
			Name:        name,
			SourceExpr:  nil,
			VersionExpr: nil,
			DeclRange:   attr.Expr.Range(),
		}
		var sourceExpr, versionExpr hcl.Expression

	LOOP:
		for _, kv := range kvs {
			key, keyDiags := kv.Key.Value(nil)
			if keyDiags.HasErrors() {
				diags = append(diags, keyDiags...)
				continue
			}

			if key.Type() != cty.String {
				diags = append(diags, &hcl.Diagnostic{
					Severity: hcl.DiagError,
					Summary:  "Invalid Attribute",
					Detail:   fmt.Sprintf("Invalid attribute value for provider requirement: %#v", key),
					Subject:  kv.Key.Range().Ptr(),
				})
				continue
			}

			switch key.AsString() {
			case "version":
				versionExpr = kv.Value
				providerExpr.VersionExpr = kv.Value

			case "source":
				sourceExpr = kv.Value
				providerExpr.SourceExpr = kv.Value

			case "configuration_aliases":
				exprs, listDiags := hcl.ExprList(kv.Value)
				if listDiags.HasErrors() {
					diags = append(diags, listDiags...)
					continue
				}

				for _, expr := range exprs {
					traversal, travDiags := hcl.AbsTraversalForExpr(expr)
					if travDiags.HasErrors() {
						diags = append(diags, travDiags...)
						continue
					}

					addr, cfgDiags := ParseProviderConfigCompact(traversal)
					if cfgDiags.HasErrors() {
						diags = append(diags, &hcl.Diagnostic{
							Severity: hcl.DiagError,
							Summary:  "Invalid configuration_aliases value",
							Detail:   `Configuration aliases can only contain references to local provider configuration names in the format of provider.alias`,
							Subject:  kv.Value.Range().Ptr(),
						})
						continue
					}

					if addr.LocalName != name {
						diags = append(diags, &hcl.Diagnostic{
							Severity: hcl.DiagError,
							Summary:  "Invalid configuration_aliases value",
							Detail:   fmt.Sprintf(`Configuration aliases must be prefixed with the provider name. Expected %q, but found %q.`, name, addr.LocalName),
							Subject:  kv.Value.Range().Ptr(),
						})
						continue
					}

					rp.Aliases = append(rp.Aliases, addr)
				}

			default:
				diags = append(diags, &hcl.Diagnostic{
					Severity: hcl.DiagError,
					Summary:  "Invalid required_providers object",
					Detail:   `required_providers objects can only contain "version", "source" and "configuration_aliases" attributes. To configure a provider, use a "provider" block.`,
					Subject:  kv.Key.Range().Ptr(),
				})
				break LOOP
			}

		}

		if diags.HasErrors() {
			continue
		}

		// Provider Expression contains either source or version expression.
		// Hydrate the rest, store it into the result map and skip adding it to
		// required providers.
		if !providerExpr.IsEmpty() {
			providerExpr.ConfigAliases = rp.Aliases

			if providerExpr.SourceExpr == nil {
				providerExpr.SourceExpr = sourceExpr
			}

			if providerExpr.VersionExpr == nil {
				providerExpr.VersionExpr = versionExpr
			}

			if deferredExprs == nil {
				deferredExprs = map[string]*ProviderRequirementExpr{}
			}
			deferredExprs[name] = providerExpr

			// Skip adding it to required providers.
			continue
		}

		// We can add the required provider when there are no errors.
		// If a source was not given, create an implied type.
		if rp.Type.IsZero() {
			pType, err := addrs.ParseProviderPart(rp.Name)
			if err != nil {
				diags = append(diags, &hcl.Diagnostic{
					Severity: hcl.DiagError,
					Summary:  "Invalid provider name",
					Detail:   err.Error(),
					Subject:  attr.Expr.Range().Ptr(),
				})
			} else {
				rp.Type = addrs.ImpliedProviderForUnqualifiedType(pType)
			}
		}

		ret.RequiredProviders[rp.Name] = rp
	}

	return ret, deferredExprs, diags
}
```

### Buggy: 1 (Commit: 0a0a20afef9c0f9180592000e6ab3193914f736d)
**Repo**: moby
```go
func BenchmarkDiffBase(b *testing.B) {
	graphtest.DriverBenchDiffBase(b, driverName)
}
```

### Buggy: 1 (Commit: 0a0a20afef9c0f9180592000e6ab3193914f736d)
**Repo**: moby
```go
func BenchmarkRead20Layers(b *testing.B) {
	graphtest.DriverBenchDeepLayerRead(b, 20, driverName)
}
```

### Buggy: 1 (Commit: af18caa8f51d6931de180d654c32fd72245f6f2c)
**Repo**: etcd
```go
func (t *Trace) logInfo(threshold time.Duration) (string, []zap.Field) {
	endTime := time.Now()
	totalDuration := endTime.Sub(t.startTime)
	traceNum := rand.Int31()
	msg := fmt.Sprintf("trace[%d] %s", traceNum, t.operation)

	var steps []string
	lastStepTime := t.startTime
	for i := 0; i < len(t.steps); i++ {
		tstep := t.steps[i]
		// add subtrace common fields which defined at the beginning to each sub-steps
		if tstep.isSubTraceStart {
			for j := i + 1; j < len(t.steps) && !t.steps[j].isSubTraceEnd; j++ {
				t.steps[j].fields = append(tstep.fields, t.steps[j].fields...)
			}
			continue
		}
		// add subtrace common fields which defined at the end to each sub-steps
		if tstep.isSubTraceEnd {
			for j := i - 1; j >= 0 && !t.steps[j].isSubTraceStart; j-- {
				t.steps[j].fields = append(tstep.fields, t.steps[j].fields...)
			}
			continue
		}
	}
	for i := 0; i < len(t.steps); i++ {
		tstep := t.steps[i]
		if tstep.isSubTraceStart || tstep.isSubTraceEnd {
			continue
		}
		stepDuration := tstep.time.Sub(lastStepTime)
		if stepDuration > threshold {
			steps = append(steps, fmt.Sprintf("trace[%d] '%v' %s (duration: %v)",
				traceNum, tstep.msg, writeFields(tstep.fields), stepDuration))
		}
		lastStepTime = tstep.time
	}

	fs := []zap.Field{
		zap.String("detail", writeFields(t.fields)),
		zap.Duration("duration", totalDuration),
		zap.Time("start", t.startTime),
		zap.Time("end", endTime),
		zap.Strings("steps", steps),
		zap.Int("step_count", len(steps)),
	}
	return msg, fs
}
```

### Buggy: 1 (Commit: 6e3a0c927953dcbe8515816ffd7b1488b136d558)
**Repo**: prometheus
```go
func(tst testInput) {
		opts := &ManagerOptions{
			QueryFunc:       EngineQueryFunc(ng, storage),
			Appendable:      storage,
			Queryable:       storage,
			Context:         context.Background(),
			Logger:          promslog.NewNopLogger(),
			NotifyFunc:      func(context.Context, string, ...*Alert) {},
			OutageTolerance: 30 * time.Minute,
			ForGracePeriod:  10 * time.Minute,
		}

		activeAlert := &Alert{
			State:    StateFiring,
			ActiveAt: time.Now(),
		}

		m := map[uint64]*Alert{}
		m[1] = activeAlert

		rule := &AlertingRule{
			name:                "HTTPRequestRateLow",
			vector:              expr,
			holdDuration:        5 * time.Minute,
			labels:              labels.FromStrings("severity", "critical"),
			annotations:         labels.EmptyLabels(),
			externalLabels:      nil,
			externalURL:         "",
			active:              m,
			logger:              nil,
			restored:            atomic.NewBool(true),
			health:              atomic.NewString(string(HealthUnknown)),
			evaluationTimestamp: atomic.NewTime(time.Time{}),
			evaluationDuration:  atomic.NewDuration(0),
			lastError:           atomic.NewError(nil),
		}

		group := NewGroup(GroupOptions{
			Name:              "default",
			Interval:          time.Second,
			Rules:             []Rule{rule},
			ShouldRestore:     true,
			Opts:              opts,
			EvalIterationFunc: tst.evalIterationFunc,
		})

		go func() {
			group.run(opts.Context)
		}()

		time.Sleep(3 * time.Second)
		group.stop()

		require.Equal(t, tst.expectedValue, testValue)
		if tst.lastEvalTimestampIsZero {
			require.Zero(t, group.GetLastEvalTimestamp())
		} else {
			oneMinute, _ := time.ParseDuration("1m")
			require.WithinDuration(t, time.Now(), group.GetLastEvalTimestamp(), oneMinute)
		}
	}
```

### Buggy: 0 (Commit: b638eb2a589e9b1d72cbdc98c9ad3de9378a9fe8)
**Repo**: etcd
```go
func() {
			require.NoError(t, gofail.Disable(options.failpoint.name))
		}
```

### Buggy: 1 (Commit: f081a1ab32936811de27657f5f31d9539db2c56e)
**Repo**: go
```go
func (x Int32x4) Permute(indices Uint32x4) (z Int32x4) {
	return Int32x4{spec.Permute[int32, spec.Width128, uint32](x.v, indices.v)}
}
```

### Buggy: 1 (Commit: 9d3d6b485c0366b79650b387d9b7b19b8a7cd034)
**Repo**: moby
```go
func (md MD) Copy() MD {
	out := make(MD, len(md))
	for k, v := range md {
		out[k] = copyOf(v)
	}
	return out
}
```

### Buggy: 1 (Commit: 68c94e2f87e393e5dcb8bcb4df40b5fa33f44ef1)
**Repo**: prometheus
```go
func lexDurationExpr(l *Lexer) stateFn {
	switch r := l.next(); {
	case r == eof:
		return l.errorf("unexpected end of input in duration expression")
	case r == ']':
		l.emit(RIGHT_BRACKET)
		l.bracketOpen = false
		l.gotColon = false
		return lexStatements
	case r == ':':
		l.emit(COLON)
		if !l.gotDuration {
			return l.errorf("unexpected colon before duration in duration expression")
		}
		if l.gotColon {
			return l.errorf("unexpected repeated colon in duration expression")
		}
		l.gotColon = true
		return lexDurationExpr
	case r == '(':
		l.emit(LEFT_PAREN)
		l.parenDepth++
		return lexDurationExpr
	case r == ')':
		l.emit(RIGHT_PAREN)
		l.parenDepth--
		if l.parenDepth < 0 {
			return l.errorf("unexpected right parenthesis %q", r)
		}
		return lexDurationExpr
	case isSpace(r):
		skipSpaces(l)
		return lexDurationExpr
	case r == '+':
		l.emit(ADD)
		return lexDurationExpr
	case r == '-':
		l.emit(SUB)
		return lexDurationExpr
	case r == '*':
		l.emit(MUL)
		return lexDurationExpr
	case r == '/':
		l.emit(DIV)
		return lexDurationExpr
	case r == '%':
		l.emit(MOD)
		return lexDurationExpr
	case r == '^':
		l.emit(POW)
		return lexDurationExpr
	case r == ',':
		l.emit(COMMA)
		return lexDurationExpr
	case isDurationKeywordStartChar(r):
		if l.scanDurationKeyword() {
			return lexDurationExpr
		}
		return l.errorf("unexpected character in duration expression: %q", r)
	case isDigit(r) || (r == '.' && isDigit(l.peek())):
		l.backup()
		l.gotDuration = true
		return lexNumberOrDuration
	default:
		return l.errorf("unexpected character in duration expression: %q", r)
	}
}
```

### Buggy: 1 (Commit: 6e4476b9d61979a60bbb8038394988ccb08eb36c)
**Repo**: go
```go
func(t *testing.T) {
			got := tt.req.ExportIsReplayable()
			if got != tt.want {
				t.Errorf("replyable = %v; want %v", got, tt.want)
			}
		}
```

### Buggy: 0 (Commit: d19e0a4b74343279d34cb19b796bf817e5bdc679)
**Repo**: hugo
```go
func TestPagesFromGoTmplTermIsEmpty(t *testing.T) {
	t.Parallel()

	files := `
-- hugo.toml --
baseURL = "https://example.com"
disableKinds = ['section', 'home', 'rss','sitemap']
printPathWarnings = true
[taxonomies]
tag = "tags"
-- content/mypost.md --
---
title: "My Post"
tags: ["mytag"]
---
-- content/tags/_content.gotmpl --
{{ .AddPage (dict "path" "mothertag" "title" "My title" "kind" "term") }}
--
-- layouts/taxonomy.html --
Terms: {{ range .Data.Terms.ByCount }}{{ .Name }}: {{ .Count }}|{{ end }}§s
-- layouts/single.html --
Single.
`

	b := hugolib.Test(t, files, hugolib.TestOptWarn())

	b.AssertFileContent("public/tags/index.html", "Terms: mytag: 1|§s")
}
```

### Buggy: 1 (Commit: fbba4f46e4fc0fe36f8fca6553fe4cade9c1dfc3)
**Repo**: etcd
```go
func (a *uberApplier) Apply(r *pb.InternalRaftRequest, shouldApplyV3 membership.ShouldApplyV3) *Result {
	// We first execute chain of Apply() calls down the hierarchy:
	// (i.e. CorruptApplier -> CappedApplier -> Auth -> Quota -> Backend),
	// then dispatch() unpacks the request to a specific method (like Put),
	// that gets executed down the hierarchy again:
	// i.e. CorruptApplier.Put(CappedApplier.Put(...(BackendApplier.Put(...)))).
	return a.applyV3.Apply(r, shouldApplyV3, a.dispatch)
}
```

### Buggy: 0 (Commit: b917b14ff9d189f16a7492be79d123a47806ee19)
**Repo**: gin
```go
func TestMappingCollectionFormat(t *testing.T) {
	var s struct {
		SliceMulti []int  `form:"slice_multi" collection_format:"multi"`
		SliceCsv   []int  `form:"slice_csv" collection_format:"csv"`
		SliceSsv   []int  `form:"slice_ssv" collection_format:"ssv"`
		SliceTsv   []int  `form:"slice_tsv" collection_format:"tsv"`
		SlicePipes []int  `form:"slice_pipes" collection_format:"pipes"`
		ArrayMulti [2]int `form:"array_multi" collection_format:"multi"`
		ArrayCsv   [2]int `form:"array_csv" collection_format:"csv"`
		ArraySsv   [2]int `form:"array_ssv" collection_format:"ssv"`
		ArrayTsv   [2]int `form:"array_tsv" collection_format:"tsv"`
		ArrayPipes [2]int `form:"array_pipes" collection_format:"pipes"`
	}
	err := mappingByPtr(&s, formSource{
		"slice_multi": {"1", "2"},
		"slice_csv":   {"1,2"},
		"slice_ssv":   {"1 2"},
		"slice_tsv":   {"1	2"},
		"slice_pipes": {"1|2"},
		"array_multi": {"1", "2"},
		"array_csv":   {"1,2"},
		"array_ssv":   {"1 2"},
		"array_tsv":   {"1	2"},
		"array_pipes": {"1|2"},
	}, "form")
	require.NoError(t, err)

	assert.Equal(t, []int{1, 2}, s.SliceMulti)
	assert.Equal(t, []int{1, 2}, s.SliceCsv)
	assert.Equal(t, []int{1, 2}, s.SliceSsv)
	assert.Equal(t, []int{1, 2}, s.SliceTsv)
	assert.Equal(t, []int{1, 2}, s.SlicePipes)
	assert.Equal(t, [2]int{1, 2}, s.ArrayMulti)
	assert.Equal(t, [2]int{1, 2}, s.ArrayCsv)
	assert.Equal(t, [2]int{1, 2}, s.ArraySsv)
	assert.Equal(t, [2]int{1, 2}, s.ArrayTsv)
	assert.Equal(t, [2]int{1, 2}, s.ArrayPipes)
}
```

