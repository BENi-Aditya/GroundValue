"""Private, versioned workspace persistence for a small single-team Vercel deployment.

Immutable SQLite snapshots avoid stale CDN reads. A conditional Blob creation lock
serializes requests across instances. This is a submission workspace, not a
replacement for a transactional multi-tenant database at production scale.
"""
import os,time,tempfile,hashlib,uuid
from pathlib import Path
from flask import g,request,jsonify
import projects

class StorageBusy(RuntimeError): pass

class WorkspaceStore:
    def __init__(self,blob=None):
        if blob is None:
            from vercel.blob import sync as blob
        self.blob=blob
        env=os.environ.get('VERCEL_ENV','development')
        self.prefix='workspace-v1/'+env+'/'
        self.lock=self.prefix+'request.lock'
        self.etag=None;self.acquired=0;self.digest=None;self.directory=None
    def open(self):
        from vercel.blob import BlobNotFoundError
        deadline=time.monotonic()+8
        while True:
            try:
                result=self.blob.put_blob(self.lock,str(time.time()).encode(),access='private',allow_overwrite=False)
                self.etag=result.etag;self.acquired=time.monotonic();break
            except Exception:
                try:
                    meta=self.blob.head_blob(self.lock)
                    if time.time()-meta.uploaded_at.timestamp()>360:
                        self.blob.delete_blob(self.lock,if_match=meta.etag)
                        continue
                except BlobNotFoundError:
                    pass
                except Exception:
                    raise StorageBusy('Private storage is temporarily unavailable. Please retry.') from None
                if time.monotonic()>deadline:
                    raise StorageBusy('The workspace is saving another request. Please retry in a moment.') from None
                time.sleep(.4)
        self.directory=tempfile.TemporaryDirectory(prefix='groundvalue-')
        self.path=Path(self.directory.name)/'workspace.sqlite3'
        entries=list(self.blob.query_blob_entries(prefix=self.prefix+'snapshots/'))
        if entries:
            latest=max(entries,key=lambda x:x.pathname)
            self.path.write_bytes(self.blob.get_blob(latest.url,access='private').body)
        self.digest=self.hash()
        self.context=projects.REQUEST_DB.set(self.path)
        return self
    def hash(self):
        return hashlib.sha256(self.path.read_bytes()).hexdigest() if self.path.exists() else None
    def checkpoint(self):
        digest=self.hash()
        if digest==self.digest:return
        if time.monotonic()-self.acquired>280:
            raise StorageBusy('This request took too long to save safely. Refresh before retrying.')
        meta=self.blob.head_blob(self.lock)
        if meta.etag!=self.etag:raise StorageBusy('Workspace lock changed. Refresh before retrying.')
        name=f'{self.prefix}snapshots/{time.time_ns():020d}-{uuid.uuid4().hex}.sqlite3'
        self.blob.put_blob(name,self.path.read_bytes(),access='private',content_type='application/octet-stream')
        self.digest=digest
    def close(self):
        if hasattr(self,'context'):projects.REQUEST_DB.reset(self.context)
        if self.directory:self.directory.cleanup()
        if self.etag:
            try:self.blob.delete_blob(self.lock,if_match=self.etag)
            except Exception:pass
            self.etag=None

def checkpoint():
    if hasattr(g,'workspace_store'):g.workspace_store.checkpoint()

def install(app):
    @app.before_request
    def restore_workspace():
        if not request.path.startswith('/api/') or request.path=='/api/session':return
        store=WorkspaceStore();g.workspace_store=store
        try:store.open()
        except Exception:
            store.close()
            return jsonify(error='Private storage is busy or unavailable. Please retry shortly.'),503
    @app.after_request
    def persist_workspace(response):
        store=getattr(g,'workspace_store',None)
        if store and hasattr(store,'context'):
            try:
                # Save state even for a provider error so a paid run is never silently replayed.
                store.checkpoint()
            except Exception:
                return jsonify(error='The latest change could not be saved. Check the workspace before retrying.'),503
        return response
    @app.teardown_request
    def release_workspace(error):
        store=getattr(g,'workspace_store',None)
        if store:store.close()
